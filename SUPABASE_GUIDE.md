# Using the API with Supabase Storage

The Voice Dementia Detection API supports audio files hosted on Supabase Storage. This guide shows you how to use it.

## Supabase URL Types

### 1. Public URLs (No Authentication Required)

If your Supabase storage bucket is set to **public**, you can use the public URL directly:

```
https://your-project-id.supabase.co/storage/v1/object/public/bucket-name/audio-file.mp3
```

**Example API call:**
```bash
curl -X POST "http://localhost:8000/predict/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.supabase.co/storage/v1/object/public/audio/patient-voice.mp3"}'
```

### 2. Signed URLs (Temporary Access)

Supabase signed URLs include authentication in the URL itself:

```
https://your-project-id.supabase.co/storage/v1/object/sign/bucket-name/audio-file.mp3?token=eyJhbGc...
```

**Example API call:**
```bash
curl -X POST "http://localhost:8000/predict/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.supabase.co/storage/v1/object/sign/audio/patient-voice.mp3?token=eyJhbGc..."}'
```

### 3. Authenticated URLs (Bearer Token)

For private buckets, you can provide a Bearer token:

**Example API call:**
```bash
curl -X POST "http://localhost:8000/predict/url" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-supabase-anon-key" \
  -d '{"url": "https://your-project.supabase.co/storage/v1/object/public/audio/patient-voice.mp3"}'
```

## Python Examples

### Using Public URL

```python
import requests

url = "http://localhost:8000/predict/url"
supabase_url = "https://your-project.supabase.co/storage/v1/object/public/audio/patient-voice.mp3"

response = requests.post(
    url,
    json={"url": supabase_url}
)

result = response.json()
print(f"Result: {result['result']}")
print(f"Dementia Probability: {result['probabilities']['dementia_percentage']}%")
```

### Using Signed URL

```python
import requests

url = "http://localhost:8000/predict/url"
# Signed URL from Supabase (includes token in query string)
signed_url = "https://your-project.supabase.co/storage/v1/object/sign/audio/patient-voice.mp3?token=eyJhbGc..."

response = requests.post(
    url,
    json={"url": signed_url}
)

result = response.json()
print(result)
```

### Using Authenticated Request

```python
import requests

url = "http://localhost:8000/predict/url"
supabase_url = "https://your-project.supabase.co/storage/v1/object/public/audio/patient-voice.mp3"
supabase_key = "your-supabase-anon-key-or-service-role-key"

response = requests.post(
    url,
    json={"url": supabase_url},
    headers={"Authorization": f"Bearer {supabase_key}"}
)

result = response.json()
print(result)
```

## JavaScript/TypeScript Examples

### Using Public URL

```javascript
const apiUrl = 'http://localhost:8000/predict/url';
const supabaseUrl = 'https://your-project.supabase.co/storage/v1/object/public/audio/patient-voice.mp3';

fetch(apiUrl, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ url: supabaseUrl })
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.result);
  console.log('Dementia Probability:', data.probabilities.dementia_percentage + '%');
});
```

### Using Supabase Client (Frontend)

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient('https://your-project.supabase.co', 'your-anon-key');

// Get public URL
const { data } = supabase
  .storage
  .from('audio')
  .getPublicUrl('patient-voice.mp3');

// Call API with public URL
fetch('http://localhost:8000/predict/url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: data.publicUrl })
})
.then(res => res.json())
.then(result => console.log(result));
```

### Using Signed URL (Frontend)

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient('https://your-project.supabase.co', 'your-anon-key');

// Get signed URL (valid for 1 hour by default)
const { data, error } = await supabase
  .storage
  .from('audio')
  .createSignedUrl('patient-voice.mp3', 3600); // 1 hour expiry

if (data) {
  // Call API with signed URL
  const response = await fetch('http://localhost:8000/predict/url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: data.signedUrl })
  });
  
  const result = await response.json();
  console.log(result);
}
```

## Supabase Storage Setup

### 1. Create a Storage Bucket

```sql
-- In Supabase SQL Editor or via Dashboard
-- Create a bucket for audio files
INSERT INTO storage.buckets (id, name, public)
VALUES ('audio', 'audio', true); -- Set to false for private bucket
```

### 2. Upload Audio Files

```javascript
// Using Supabase JS client
const { data, error } = await supabase.storage
  .from('audio')
  .upload('patient-voice.mp3', file, {
    contentType: 'audio/mpeg',
    upsert: false
  });
```

### 3. Get File URL

**Public bucket:**
```javascript
const { data } = supabase.storage
  .from('audio')
  .getPublicUrl('patient-voice.mp3');

console.log(data.publicUrl);
```

**Private bucket (signed URL):**
```javascript
const { data } = await supabase.storage
  .from('audio')
  .createSignedUrl('patient-voice.mp3', 3600);

console.log(data.signedUrl);
```

## Error Handling

The API will return appropriate error codes:

- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: Access denied (bucket is private and no valid auth provided)
- **404 Not Found**: File doesn't exist at the URL
- **500 Internal Server Error**: Other errors (network, processing, etc.)

**Example error response:**
```json
{
  "detail": "Unauthorized: Invalid or missing authentication token. For Supabase, provide a valid Bearer token."
}
```

## Security Best Practices

1. **Use Signed URLs**: For private files, generate signed URLs with short expiration times
2. **Use Service Role Key**: For server-side access, use the service role key (keep it secret!)
3. **Use Anon Key**: For client-side access, use the anon key (it's safe to expose)
4. **Set Bucket Policies**: Configure RLS (Row Level Security) policies on your storage bucket
5. **Validate URLs**: Ensure URLs are from your Supabase project domain

## Complete Example: Full Workflow

```javascript
// 1. Upload audio to Supabase
const file = document.getElementById('audioFile').files[0];
const { data: uploadData, error: uploadError } = await supabase.storage
  .from('audio')
  .upload(`${Date.now()}-${file.name}`, file);

if (uploadError) {
  console.error('Upload error:', uploadError);
  return;
}

// 2. Get public URL
const { data: urlData } = supabase.storage
  .from('audio')
  .getPublicUrl(uploadData.path);

// 3. Analyze with API
const response = await fetch('http://localhost:8000/predict/url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: urlData.publicUrl })
});

const result = await response.json();

// 4. Display results
console.log('Analysis Result:', result.result);
console.log('Dementia Probability:', result.probabilities.dementia_percentage + '%');
console.log('Normal Probability:', result.probabilities.normal_percentage + '%');
```

## Testing

Test with a Supabase URL:

```bash
# Replace with your actual Supabase URL
curl -X POST "http://localhost:8000/predict/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-project.supabase.co/storage/v1/object/public/audio/test.mp3"
  }'
```

The API will download the file from Supabase, process it, and return the analysis results!

