//
//Used HttpClient for making HTTP requests.
//async and await are used to handle asynchronous requests.
//Error handling is done with exceptions.
//JSON serialization and deserialization is handled by System.Text.Json.
//The Python requests.Session() behavior is mapped to HttpClient, which persists across multiple requests.
//
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class IrDataClient2
{
    private bool authenticated;
    private HttpClient client;
    private string baseUrl;
    private string username;
    private string encodedPassword;

    public IrDataClient(string username, string password)
    {
        authenticated = false;
        client = new HttpClient();
        baseUrl = "https://members-ng.iracing.com";
        this.username = username;
        encodedPassword = EncodePassword(username, password);
    }

    private string EncodePassword(string username, string password)
    {
        using (SHA256 sha256 = SHA256.Create())
        {
            byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password + username.ToLower()));
            return Convert.ToBase64String(hashBytes);
        }
    }

    private async Task<string> LoginAsync()
    {
        var headers = new Dictionary<string, string> { { "Content-Type", "application/json" } };
        var data = new { email = username, password = encodedPassword };
        var content = new StringContent(JsonSerializer.Serialize(data), Encoding.UTF8, "application/json");

        try
        {
            HttpResponseMessage response = await client.PostAsync($"{baseUrl}/auth", content);
            if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                Console.WriteLine("Rate limited, waiting");
                if (response.Headers.Contains("x-ratelimit-reset"))
                {
                    string ratelimitReset = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
                    if (long.TryParse(ratelimitReset, out long resetTimestamp))
                    {
                        DateTime resetDatetime = DateTimeOffset.FromUnixTimeSeconds(resetTimestamp).DateTime;
                        TimeSpan delta = resetDatetime - DateTime.Now;
                        if (delta.TotalSeconds > 0)
                            await Task.Delay(delta);
                    }
                }
                return await LoginAsync();
            }
            else if (response.IsSuccessStatusCode)
            {
                var responseData = JsonSerializer.Deserialize<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
                if (responseData.ContainsKey("authcode"))
                {
                    authenticated = true;
                    return "Logged in";
                }
            }
            else
            {
                throw new Exception($"Error from iRacing: {await response.Content.ReadAsStringAsync()}");
            }
        }
        catch (TaskCanceledException)
        {
            throw new Exception("Login timed out");
        }
        catch (HttpRequestException)
        {
            throw new Exception("Connection error");
        }

        return null;
    }

    private string BuildUrl(string endpoint)
    {
        return $"{baseUrl}{endpoint}";
    }

    private async Task<Dictionary<string, object>> GetResourceOrLinkAsync(string url, Dictionary<string, string> payload = null)
    {
        if (!authenticated)
        {
            await LoginAsync();
            return await GetResourceOrLinkAsync(url, payload);
        }

        var queryString = payload != null ? $"?{string.Join("&", payload.Select(kv => $"{kv.Key}={kv.Value}"))}" : string.Empty;
        HttpResponseMessage response = await client.GetAsync(url + queryString);

        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
        {
            authenticated = false;
            return await GetResourceOrLinkAsync(url, payload);
        }
        else if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
        {
            Console.WriteLine("Rate limited, waiting");
            if (response.Headers.Contains("x-ratelimit-reset"))
            {
                string ratelimitReset = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
                if (long.TryParse(ratelimitReset, out long resetTimestamp))
                {
                    DateTime resetDatetime = DateTimeOffset.FromUnixTimeSeconds(resetTimestamp).DateTime;
                    TimeSpan delta = resetDatetime - DateTime.Now;
                    if (delta.TotalSeconds > 0)
                        await Task.Delay(delta);
                }
            }
            return await GetResourceOrLinkAsync(url, payload);
        }
        else if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"Unhandled Non-200 response: {response.StatusCode}");
        }

        var data = JsonSerializer.Deserialize<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());

        if (!data.ContainsKey("link"))
        {
            return data;
        }
        else
        {
            string link = data["link"].ToString();
            return new Dictionary<string, object> { { "link", link } };
        }
    }

    public async Task<Dictionary<string, object>> GetResourceAsync(string endpoint, Dictionary<string, string> payload = null)
    {
        string requestUrl = BuildUrl(endpoint);
        var resourceObj = await GetResourceOrLinkAsync(requestUrl, payload);

        if (resourceObj.ContainsKey("link"))
        {
            HttpResponseMessage response = await client.GetAsync(resourceObj["link"].ToString());

            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                authenticated = false;
                return await GetResourceAsync(endpoint, payload);
            }
            else if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                Console.WriteLine("Rate limited, waiting");
                if (response.Headers.Contains("x-ratelimit-reset"))
                {
                    string ratelimitReset = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
                    if (long.TryParse(ratelimitReset, out long resetTimestamp))
                    {
                        DateTime resetDatetime = DateTimeOffset.FromUnixTimeSeconds(resetTimestamp).DateTime;
                        TimeSpan delta = resetDatetime - DateTime.Now;
                        if (delta.TotalSeconds > 0)
                            await Task.Delay(delta);
                    }
                }
                return await GetResourceAsync(endpoint, payload);
            }

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"Unhandled Non-200 response: {response.StatusCode}");
            }

            return JsonSerializer.Deserialize<Dictionary<string, object>>(await response.Content.ReadAsStringAsync());
        }

        return resourceObj;
    }

    public async Task<List<Dictionary<string, object>>> GetCarsAsync()
    {
        return await GetResourceAsync("/data/car/get") as List<Dictionary<string, object>>;
    }

    public async Task<List<Dictionary<string, object>>> GetTracksAsync()
    {
        return await GetResourceAsync("/data/track/get") as List<Dictionary<string, object>>;
    }

    // Similarly, you can implement other methods
}
