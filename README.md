# OpenCV 人臉情緒辨識原型

這個原型會做三件事：

1. 開啟電腦攝影機
2. 偵測人臉
3. 使用 FER+ ONNX 模型預測 7 類基本情緒

## 目前輸出情緒類別

- neutral
- happiness
- sadness
- anger
- disgust
- fear
- contempt

## 執行方式

在工作區根目錄執行：

```powershell
& ".venv/Scripts/python.exe" -m pip install -r requirements.txt
```

然後執行：

```powershell
& ".venv/Scripts/python.exe" emotion_camera.py
```

如果要指定其他攝影機：

```powershell
& ".venv/Scripts/python.exe" emotion_camera.py --camera 1
```

如果你不想要鏡像反轉（預設為開啟）：

```powershell
& ".venv/Scripts/python.exe" emotion_camera.py --no-mirror
```

如果你覺得人臉不夠靈敏，可以再降低最小臉尺寸：

```powershell
& ".venv/Scripts/python.exe" emotion_camera.py --min-face 36
```

如果你覺得情緒結果不穩定，建議用這組參數：

```powershell
& ".venv/Scripts/python.exe" emotion_camera.py --min-face 36 --smooth-alpha 0.22 --confidence-threshold 0.5 --face-padding 0.22 --neutral-penalty 0.5 --emotion-boost 1.3
```

## 15 秒情緒回傳

- 程式會每秒輸出 15 秒統計結果到 emotion_output/latest_emotion.json
- 欄位包含 dominant_emotion、dominant_share、vote_ratios、probability_ratios

## PHP + Spotify 網頁

1. 先啟動情緒辨識程式（讓 JSON 持續更新）
2. 設定 spotify_config.php 內的 client_id / client_secret
3. 雙擊 run_web.bat 或執行下列指令啟動網站：

```powershell
& "C:/xampp/php/php.exe" -S 127.0.0.1:8080
```

4. 瀏覽器打開 http://127.0.0.1:8080

## 注意事項

- 第一次執行會自動下載 FER+ 模型到 models/emotion-ferplus-8.onnx
- 建議單人入鏡、正面面對鏡頭、光線穩定
- 預設已調成較靈敏的人臉偵測；若距離鏡頭較遠可把 --min-face 再調小
- 目前有加入時間平滑與低信心保守輸出，低於門檻會顯示 uncertain
- PHP 網頁的 Spotify 推薦使用多語系、多曲風 query，避免只偏英文流行歌
- 這是專題原型，適合做即時情緒傾向判斷，不適合拿來當心理診斷工具