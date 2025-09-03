param(
  [string]$PromptPath = "docs/prompts/generate_report_prompt.md"
)

if (!(Test-Path $PromptPath)) {
  Write-Error "Prompt not found: $PromptPath"
  exit 1
}

Write-Host "===== BEGIN PROMPT: $PromptPath ====="
Get-Content -Path $PromptPath | ForEach-Object { $_ }
Write-Host "`n===== END PROMPT ====="
