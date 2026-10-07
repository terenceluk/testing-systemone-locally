# Times the same three-question request against whichever decision model is loaded.
# One warm-up request is sent first and discarded, then the timed runs follow.
# The times include PowerShell's own HTTP overhead, which matters for a model as fast as Laya.
param(
    [string]$Uri = "http://localhost:8080/v1/systemone",
    [int]$Runs = 10
)

# Stop at the first failed request, so a server that is not running is reported and not timed.
$ErrorActionPreference = "Stop"

$body = @'
{
  "state": "Customer message: I was charged twice for my order last week and nobody has replied.",
  "questions": {
    "route": {
      "type": "choice",
      "instructions": "Which team should handle this?",
      "criteria": {
        "billing": "payments, charges, refunds, invoices",
        "shipping": "delivery, tracking, lost or late parcels",
        "technical": "bugs, errors, login problems"
      }
    },
    "angry": {
      "type": "noul",
      "instructions": "Is the customer angry?"
    },
    "urgency": {
      "type": "score",
      "instructions": "How urgent is this?",
      "criteria": [
        "can wait",
        "this week",
        "today",
        "right now"
      ]
    }
  }
}
'@

Invoke-RestMethod -Uri $Uri -Method Post -ContentType "application/json" -Body $body | Out-Null

$timings = 1..$Runs | ForEach-Object {
    (Measure-Command {
        Invoke-RestMethod -Uri $Uri -Method Post -ContentType "application/json" -Body $body
    }).TotalMilliseconds
}

$sorted = @($timings | Sort-Object)
$mid = [int][math]::Floor($sorted.Count / 2)
$median = if ($sorted.Count % 2) { $sorted[$mid] } else { ($sorted[$mid - 1] + $sorted[$mid]) / 2 }

"Fastest: {0:N0} ms" -f $sorted[0]
"Median:  {0:N0} ms" -f $median
"Slowest: {0:N0} ms" -f $sorted[-1]
