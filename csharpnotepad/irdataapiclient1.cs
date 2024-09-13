//-->ChatGPT
//I've replaced Python's requests library with HttpClient in C# for making HTTP requests.
//The encode_password method uses C#'s SHA256 and Base64 classes for hashing and encoding.
//Methods were converted into async C# methods using Task and await to handle asynchronous requests.
//For JSON handling, C#'s System.Text.Json is used to parse responses.
//Rate limiting, authentication retries, and chunk handling are all converted to equivalent C# constructs.
//
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;

public class IrDataClient
{
    private bool authenticated;
    private readonly HttpClient httpClient;
    private readonly string baseUrl = "https://members-ng.iracing.com";
    private readonly string username;
    private readonly string encodedPassword;

    public IrDataClient(string username, string password)
    {
        authenticated = false;
        httpClient = new HttpClient();
        this.username = username;
        this.encodedPassword = EncodePassword(username, password);
    }

    private string EncodePassword(string username, string password)
    {
        using (var sha256 = SHA256.Create())
        {
            var combined = Encoding.UTF8.GetBytes(password + username.ToLower());
            var hash = sha256.ComputeHash(combined);
            return Convert.ToBase64String(hash);
        }
    }

    private async Task<string> LoginAsync()
    {
        var headers = new Dictionary<string, string>
        {
            { "Content-Type", "application/json" }
        };
        var data = new
        {
            email = username,
            password = encodedPassword
        };

        try
        {
            var response = await httpClient.PostAsJsonAsync("https://members-ng.iracing.com/auth", data);
            if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
            {
                Console.WriteLine("Rate limited, waiting");
                var resetTime = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
                if (!string.IsNullOrEmpty(resetTime))
                {
                    var resetDateTime = DateTimeOffset.FromUnixTimeSeconds(long.Parse(resetTime)).DateTime;
                    var delta = resetDateTime - DateTime.Now;
                    if (delta.TotalSeconds > 0)
                    {
                        await Task.Delay((int)delta.TotalMilliseconds);
                    }
                }
                return await LoginAsync();
            }

            var responseData = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
            if (response.IsSuccessStatusCode && responseData.ContainsKey("authcode"))
            {
                authenticated = true;
                return "Logged in";
            }
            else
            {
                throw new Exception("Error from iRacing: " + JsonSerializer.Serialize(responseData));
            }
        }
        catch (HttpRequestException ex)
        {
            throw new Exception("Connection error", ex);
        }
        catch (TaskCanceledException)
        {
            throw new TimeoutException("Login timed out");
        }
    }

    private string BuildUrl(string endpoint)
    {
        return baseUrl + endpoint;
    }

    private async Task<(object, bool)> GetResourceOrLinkAsync(string url, Dictionary<string, string> payload = null)
    {
        if (!authenticated)
        {
            await LoginAsync();
            return await GetResourceOrLinkAsync(url, payload);
        }

        var response = await httpClient.GetAsync(url);
        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
        {
            authenticated = false;
            return await GetResourceOrLinkAsync(url, payload);
        }

        if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
        {
            Console.WriteLine("Rate limited, waiting");
            var resetTime = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
            if (!string.IsNullOrEmpty(resetTime))
            {
                var resetDateTime = DateTimeOffset.FromUnixTimeSeconds(long.Parse(resetTime)).DateTime;
                var delta = resetDateTime - DateTime.Now;
                if (delta.TotalSeconds > 0)
                {
                    await Task.Delay((int)delta.TotalMilliseconds);
                }
            }
            return await GetResourceOrLinkAsync(url, payload);
        }

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception("Unhandled Non-200 response: " + response.StatusCode);
        }

        var data = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        if (data.ContainsKey("link"))
        {
            return (data["link"], true);
        }
        else
        {
            return (data, false);
        }
    }

    public async Task<object> GetResourceAsync(string endpoint, Dictionary<string, string> payload = null)
    {
        var requestUrl = BuildUrl(endpoint);
        var (resourceObj, isLink) = await GetResourceOrLinkAsync(requestUrl, payload);

        if (!isLink)
        {
            return resourceObj;
        }

        var response = await httpClient.GetAsync(resourceObj.ToString());
        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
        {
            authenticated = false;
            return await GetResourceAsync(endpoint, payload);
        }

        if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
        {
            Console.WriteLine("Rate limited, waiting");
            var resetTime = response.Headers.GetValues("x-ratelimit-reset").FirstOrDefault();
            if (!string.IsNullOrEmpty(resetTime))
            {
                var resetDateTime = DateTimeOffset.FromUnixTimeSeconds(long.Parse(resetTime)).DateTime;
                var delta = resetDateTime - DateTime.Now;
                if (delta.TotalSeconds > 0)
                {
                    await Task.Delay((int)delta.TotalMilliseconds);
                }
            }
            return await GetResourceAsync(endpoint, payload);
        }

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception("Unhandled Non-200 response: " + response.StatusCode);
        }

        return await response.Content.ReadFromJsonAsync<object>();
    }

    private async Task<List<object>> GetChunksAsync(Dictionary<string, object> chunks)
    {
        if (chunks == null)
        {
            return new List<object>();
        }

        var baseUrl = chunks["base_download_url"].ToString();
        var urls = (chunks["chunk_file_names"] as JsonElement).EnumerateArray();
        var listOfChunks = new List<object>();

        foreach (var url in urls)
        {
            var response = await httpClient.GetFromJsonAsync<object>(baseUrl + url.GetString());
            listOfChunks.Add(response);
        }

        var output = new List<object>();
        foreach (var chunk in listOfChunks)
        {
            if (chunk is JsonElement element && element.ValueKind == JsonValueKind.Array)
            {
                output.AddRange(element.EnumerateArray());
            }
        }

        return output;
    }

    public void AddAssets(List<Dictionary<string, object>> objects, Dictionary<string, Dictionary<string, object>> assets, string idKey)
    {
        foreach (var obj in objects)
        {
            var asset = assets[obj[idKey].ToString()];
            foreach (var key in asset.Keys)
            {
                obj[key] = asset[key];
            }
        }
    }
}
