# Примеры использования функции скачивания видео

## Веб-интерфейс - Пошаговая инструкция

### 1. Основное использование (скачать полное видео)

```
1. Загрузить видео через веб-интерфейс
2. Выбрать параметры (класс объекта, метод стабилизации)
3. Нажать "Stabilize Video"
4. После завершения будет показана секция "Download Comparison Video"
5. Оставить поля "Start Frame" и "End Frame" пустыми
6. Нажать "⬇️ Download Video"
7. Видео скачается на компьютер
```

### 2. Скачать часть видео (конкретный диапазон фреймов)

```
1-4. Повторить шаги из примера 1
5. Установить Start Frame: 50
6. Установить End Frame: 250
7. Нажать "⬇️ Download Video"
8. Скачается видео с фреймов 50-250
```

### 3. Быстрое сравнение начала видео

```
1-4. Повторить шаги из примера 1
5. Установить Start Frame: 0 (или оставить пусто)
6. Установить End Frame: 100
7. Нажать "⬇️ Download Video"
```

---

## API - Примеры запросов

### Пример 1: Скачать все видео

```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  }' \
  -o stabilization_full.mp4
```

### Пример 2: Скачать определенный диапазон

```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "frame_range_start": 100,
    "frame_range_end": 300
  }' \
  -o stabilization_frames_100_300.mp4
```

### Пример 3: С использованием Python requests

```python
import requests

job_id = "550e8400-e29b-41d4-a716-446655440000"

# Скачать все видео
response = requests.post(
    "http://localhost:8000/api/download-video",
    json={"job_id": job_id}
)

if response.status_code == 200:
    with open("stabilization_full.mp4", "wb") as f:
        f.write(response.content)
    print("Видео скачано успешно!")
else:
    print(f"Ошибка: {response.json()}")

# Скачать конкретный диапазон
response = requests.post(
    "http://localhost:8000/api/download-video",
    json={
        "job_id": job_id,
        "frame_range_start": 50,
        "frame_range_end": 150
    }
)

if response.status_code == 200:
    with open("stabilization_slice.mp4", "wb") as f:
        f.write(response.content)
    print("Видео скачано успешно!")
```

### Пример 4: С использованием JavaScript/Fetch

```javascript
const jobId = "550e8400-e29b-41d4-a716-446655440000";

// Скачать все видео
fetch("http://localhost:8000/api/download-video", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        job_id: jobId
    })
})
.then(response => response.blob())
.then(blob => {
    // Создать ссылку и скачать
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stabilization_${jobId}.mp4`;
    a.click();
})
.catch(error => console.error("Ошибка:", error));

// Скачать конкретный диапазон
fetch("http://localhost:8000/api/download-video", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        job_id: jobId,
        frame_range_start: 100,
        frame_range_end: 200
    })
})
.then(response => response.blob())
.then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stabilization_${jobId}_100_200.mp4`;
    a.click();
});
```

---

## Использование в командной строке

### Скачать видео с помощью curl

```bash
# Полное видео
curl -X POST http://localhost:8000/api/download-video \
  -H "Content-Type: application/json" \
  -d '{"job_id":"my-job-id"}' \
  > output.mp4

# С прогрессбаром
curl -# -X POST http://localhost:8000/api/download-video \
  -H "Content-Type: application/json" \
  -d '{"job_id":"my-job-id"}' \
  -o output.mp4

# С диапазоном фреймов
curl -X POST http://localhost:8000/api/download-video \
  -H "Content-Type: application/json" \
  -d '{"job_id":"my-job-id","frame_range_start":10,"frame_range_end":100}' \
  -o output_slice.mp4
```

### Скачать видео с помощью wget

```bash
# Полное видео
wget --post-data='{"job_id":"my-job-id"}' \
  --header="Content-Type: application/json" \
  -O output.mp4 \
  http://localhost:8000/api/download-video
```

---

## Практические сценарии

### Сценарий 1: Анализ проблемной области

Если вы заметили проблему мерцания между фреймами 500-600:

```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "my-job-id",
    "frame_range_start": 480,
    "frame_range_end": 620
  }' \
  -o problem_area.mp4
```

Это видео будет содержать область проблемы с 40 фреймов буфера до и после.

### Сценарий 2: Создание демонстрационного видео

Для презентации результатов - скачать первые 5 секунд при 30 fps:

```bash
# 5 сек × 30 fps = 150 фреймов
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "my-job-id",
    "frame_range_start": 0,
    "frame_range_end": 150
  }' \
  -o demo_5seconds.mp4
```

### Сценарий 3: Сравнение разных методов стабилизации

1. Обработать видео методом A (Moving Average с window=5)
2. Скачать видео, сохранить как `method_a.mp4`
3. Обработать видео методом B (Median Filter с window=5)
4. Скачать видео, сохранить как `method_b.mp4`
5. Использовать ffmpeg для создания side-by-side сравнения:

```bash
ffmpeg -i method_a.mp4 -i method_b.mp4 -filter_complex "[0:v]scale=640:1440[v0];[1:v]scale=640:1440[v1];[v0][v1]hstack" \
  -c:v libx264 comparison.mp4
```

### Сценарий 4: Автоматическое скачивание в скрипте

```python
#!/usr/bin/env python3
import requests
import json
from pathlib import Path

def download_comparison_video(job_id, output_path, start_frame=None, end_frame=None):
    """
    Скачать видео сравнения стабилизации.
    
    Args:
        job_id: ID обработанного видео
        output_path: Путь для сохранения видео
        start_frame: Начальный фрейм (опционально)
        end_frame: Конечный фрейм (опционально)
    """
    
    payload = {"job_id": job_id}
    if start_frame is not None:
        payload["frame_range_start"] = start_frame
    if end_frame is not None:
        payload["frame_range_end"] = end_frame
    
    response = requests.post(
        "http://localhost:8000/api/download-video",
        json=payload,
        timeout=300  # 5 минут timeout для больших видео
    )
    
    if response.status_code == 200:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Видео скачано: {output_path}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.json())
        return False

# Использование
if __name__ == "__main__":
    # Скачать полное видео
    download_comparison_video(
        job_id="550e8400-e29b-41d4-a716-446655440000",
        output_path="output/full_comparison.mp4"
    )
    
    # Скачать конкретный диапазон
    download_comparison_video(
        job_id="550e8400-e29b-41d4-a716-446655440000",
        output_path="output/slice_100_200.mp4",
        start_frame=100,
        end_frame=200
    )
```

---

## Возможные ошибки и их решение

### Ошибка: "Job not found"

```
Причина: job_id неверный или истекший
Решение: Проверить job_id, переобработать видео
```

### Ошибка: "Cannot download video in status: segmented"

```
Причина: Стабилизация еще не завершена
Решение: Дождаться завершения обработки (статус должен быть "completed")
```

### Ошибка: "Invalid frame_range_start"

```
Причина: Начальный фрейм вне диапазона
Решение: Использовать фрейм от 0 до общего количества фреймов - 1
```

### Видео скачивается долго

```
Причины: 
- Большое видео
- Медленное соединение
- Сервер создает видео в первый раз

Решение:
- Использовать меньший диапазон фреймов
- Дождаться кэширования видео (повторные запросы быстрее)
```

---

## Дополнительные возможности

### Использование с обработкой видео

```bash
# Скачать видео, преобразовать в WebM
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"my-job-id"}' | \
  ffmpeg -i pipe:0 -c:v libvpx-vp9 -c:a libopus output.webm

# Скачать видео, создать GIF
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"my-job-id","frame_range_start":0,"frame_range_end":300}' | \
  ffmpeg -i pipe:0 -vf "scale=640:-1:flags=lanczos,split[s0][s1];[s0]palgen[p];[s1][p]paletteuse" \
  -loop 0 output.gif
```

---

**Версия:** 1.0.0  
**Последнее обновление:** December 2025
