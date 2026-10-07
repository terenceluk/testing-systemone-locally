# Sends one support ticket to a decision model and asks a choice, a noul, and a score question.
# Start a model first with serve-laya.cmd or serve-openjev.cmd.
param(
    [string]$Uri = "http://localhost:8080/v1/systemone"
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

Invoke-RestMethod `
    -Uri $Uri `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
ConvertTo-Json -Depth 10
