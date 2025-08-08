# PowerShell script for testing HackRx 6.0 API

Write-Host "🧪 Testing HackRx 6.0 API with PowerShell" -ForegroundColor Green
Write-Host "=" * 50

# Test 1: Health check
Write-Host "`n🏥 Testing health check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method GET
    Write-Host "✅ Health check successful" -ForegroundColor Green
    Write-Host "📋 Service: $($healthResponse.service)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Status check
Write-Host "`n📊 Testing status check..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/status" -Method GET
    Write-Host "✅ Status check successful" -ForegroundColor Green
    Write-Host "🔍 Index exists: $($statusResponse.index_status.index_exists)" -ForegroundColor Cyan
    Write-Host "🚀 Ready for queries: $($statusResponse.ready_for_queries)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Main API
Write-Host "`n🚀 Testing main API endpoint..." -ForegroundColor Yellow

$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
    "Authorization" = "Bearer 273418978cb9f079f5da0cd221de3a8c4ae3d5a9b29477367d3e51c2f3763444"
}

$body = @{
    documents = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    questions = @(
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "Does this policy cover maternity expenses?"
    )
} | ConvertTo-Json -Depth 10

Write-Host "📄 Document URL: $($body.documents.Substring(0, 50))..." -ForegroundColor Cyan
Write-Host "❓ Questions: $($body.questions.Count)" -ForegroundColor Cyan

try {
    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/hackrx/run" -Method POST -Headers $headers -Body $body -ContentType "application/json"
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Host "✅ API call successful!" -ForegroundColor Green
    Write-Host "⏱️  Duration: $duration seconds" -ForegroundColor Cyan
    Write-Host "📝 Answers: $($response.answers.Count)" -ForegroundColor Cyan
    
    for ($i = 0; $i -lt $response.answers.Count; $i++) {
        $answer = $response.answers[$i]
        $preview = if ($answer.Length -gt 200) { $answer.Substring(0, 200) + "..." } else { $answer }
        Write-Host "`n$($i + 1). $preview" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ API call failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "📄 Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n✅ Test completed!" -ForegroundColor Green
