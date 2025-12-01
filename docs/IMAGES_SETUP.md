# Настройка хранения изображений

## Git LFS (Large File Storage)

Этот репозиторий использует Git LFS для хранения изображений, чтобы не засорять историю Git большими бинарными файлами.

### Установка Git LFS

#### Windows
```powershell
# Через Chocolatey
choco install git-lfs

# Или скачать с https://git-lfs.github.com/
```

#### macOS
```bash
brew install git-lfs
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install git-lfs

# Fedora
sudo dnf install git-lfs
```

### Первоначальная настройка (один раз)

```bash
# Инициализация Git LFS
git lfs install

# Проверка, что LFS работает
git lfs track "*.jpg"
git lfs track "*.png"
git lfs track "*.jpeg"
git lfs track "*.gif"
git lfs track "*.webp"
```

### Работа с изображениями

После настройки Git LFS работа с изображениями ничем не отличается от обычной работы с Git:

```bash
git add images/
git commit -m "Добавлены изображения для Австрии"
git push
```

Git LFS автоматически обработает изображения.

### Проверка статуса LFS

```bash
# Проверить, какие файлы отслеживаются через LFS
git lfs ls-files

# Проверить статус LFS
git lfs status
```

### Альтернативные варианты

Если Git LFS не подходит, можно использовать:

1. **Внешнее хранилище** (GitHub Releases, Imgur, Cloudinary)
2. **Локальное хранение** (добавить `images/` в `.gitignore`)
3. **Гибридный подход** (маленькие файлы в Git, большие через LFS)

