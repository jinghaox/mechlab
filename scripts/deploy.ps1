# Build and publish to GitHub Pages (pushes the dist folder to the gh-pages branch).
# Usage: npm run deploy
# Keep this file ASCII-only: Windows PowerShell 5.1 misreads UTF-8 without a BOM.
Set-Location (Join-Path $PSScriptRoot '..')

$remote = git remote get-url origin
if (-not $remote) { Write-Host 'No "origin" remote configured.'; exit 1 }
$name = git config user.name
$email = git config user.email

npm run build
if ($LASTEXITCODE -ne 0) { Write-Host 'Build failed; nothing was published.'; exit 1 }

Push-Location dist
try {
    # .nojekyll makes GitHub Pages serve the files as-is
    New-Item -ItemType File -Name '.nojekyll' -Force | Out-Null
    git init -q -b gh-pages
    git config user.name $name
    git config user.email $email
    git add -A
    git commit -q -m "Deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push -f $remote gh-pages
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
    Remove-Item -Recurse -Force (Join-Path 'dist' '.git') -ErrorAction SilentlyContinue
}
if ($code -ne 0) { Write-Host 'Push failed.'; exit 1 }
Write-Host 'Published. The site usually updates within 1-2 minutes.'
