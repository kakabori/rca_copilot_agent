# call_rca.ps1
$uri = "http://127.0.0.1:8000/rca"

# JSONはヒアストリングにすると壊れにくい
$body = @'
{
  "asset_id": "ETCHER_01",
  "timestamp": "2026-02-15T13:05:00Z",
  "anomaly_score": 0.92,
  "top_features": ["vibration", "pressure"]
}
'@

# curl.exe を明示（PowerShellのcurlエイリアス問題を回避）
curl.exe -X POST $uri `
  -H "Content-Type: application/json" `
  -d $body