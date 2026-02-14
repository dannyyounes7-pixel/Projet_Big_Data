# Script PowerShell pour supprimer tous les emojis des fichiers markdown

$files = Get-ChildItem -Path "." -Recurse -Include *.md

# Liste des emojis courants à supprimer
$emojis = @(
    '🎯', '🚀', '✅', '📊', '🔍', '🌐', '🔐', '📁', '📈', '🔧',
    '📝', '✨', '🎓', '💡', '🐛', '📞', '🎉', '🏗️', '🗂️', '📚',
    '⚙️', '⚠️', '👥', '📄', '📹', '🏆', '🗺️', '🎬', '💻', '🔄'
)

foreach ($file in $files) {
    Write-Host "Processing: $($file.FullName)"
    
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    
    # Supprimer chaque emoji
    foreach ($emoji in $emojis) {
        $content = $content.Replace($emoji, '')
    }
    
    # Nettoyer les espaces multiples créés par la suppression
    $content = $content -replace '##\s+', '## '
    $content = $content -replace '\s{2,}', ' '
    
    # Sauvegarder seulement si le contenu a changé
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  Updated: $($file.Name)" -ForegroundColor Green
    } else {
        Write-Host "  No changes: $($file.Name)" -ForegroundColor Yellow
    }
}

Write-Host "`nDone! All emojis removed from markdown files." -ForegroundColor Cyan
