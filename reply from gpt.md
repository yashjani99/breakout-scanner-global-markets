बहुत बढ़िया। नीचे **Institutional Grade Version** का लॉजिक है जो आपके वर्तमान स्कैनर में आसानी से जोड़ सकते हैं।

## 1. Volume Breakout Filter

`cmp` निकालने के बाद यह जोड़ें:

```python
# ===========================
# Volume Breakout
# ===========================

volume = data['Volume'].squeeze()

avg_volume = volume.rolling(20).mean().iloc[-1]
today_volume = volume.iloc[-1]

volume_breakout = today_volume > (1.5 * avg_volume)
```

फिर आपकी `if` condition बदल दें:

```python
if (cmp > dma_30) and \
   (cmp > dma_50) and \
   (cmp > dma_200) and \
   (car_status == "Positive") and \
   volume_breakout:
```

---

# 2. Swing Low Stop Loss

```python
# ===========================
# Swing Low (10 Days)
# ===========================

swing_low = data['Low'].tail(10).min()

sl = min(swing_low, dma_30)
```

---

# 3. Entry Price

```python
entry = cmp
```

---

# 4. Risk

```python
risk = entry - sl

if risk <= 0:
    continue
```

---

# 5. Targets

```python
t1 = entry + (2 * risk)
t2 = entry + (3 * risk)
t3 = entry + (5 * risk)
```

---

# 6. Reward %

```python
reward_percent = ((t2-entry)/entry)*100
```

---

# 7. Stop Loss %

```python
sl_percent=((entry-sl)/entry)*100
```

---

# 8. Distance from 52 Week High

```python
high52=data['High'].tail(252).max()

dist52=((high52-entry)/high52)*100
```

---

# 9. Relative Strength (Simple)

```python
returns=(entry-close_prices.iloc[-21])/close_prices.iloc[-21]

returns=returns*100
```

---

# 10. Trend Strength

```python
if dma_30>dma_50>dma_200:
    trend="Strong Uptrend"
else:
    trend="Weak"
```

---

## Results Dictionary

`results.append()` में ये कॉलम जोड़ दें:

```python
{
'Date':today_date,
'Stock':ticker.replace('.NS',''),
'CMP':round(entry,2),
'30 DMA':round(dma_30,2),
'50 DMA':round(dma_50,2),
'200 DMA':round(dma_200,2),
'200 DMA Dist %':round(dist_200_dma,2),
'52W High Dist %':round(dist52,2),
'Volume Breakout':volume_breakout,
'Trend':trend,
'SL':round(sl,2),
'SL %':round(sl_percent,2),
'T1':round(t1,2),
'T2':round(t2,2),
'T3':round(t3,2),
'Reward %':round(reward_percent,2),
'1M Return %':round(returns,2),
'CAR Status':car_status,
'Action':action
}
```

## Final Excel Columns

आपकी Excel रिपोर्ट कुछ इस प्रकार होगी:

| Date | Stock | CMP | 30 DMA | 50 DMA | 200 DMA | Trend | Volume Breakout | SL | SL % | T1 | T2 | T3 | Reward % | 52W High Dist % | 1M Return % | CAR Status | Action |
| ---- | ----- | --: | -----: | -----: | ------: | ----- | --------------- | -: | ---: | -: | -: | -: | -------: | --------------: | ----------: | ---------- | ------ |

### अतिरिक्त सुझाव

इस स्कैनर को और भी मजबूत बनाने के लिए आप निम्न फ़िल्टर जोड़ सकते हैं:

* **RSI (14)**: केवल RSI > 55
* **ADX (14)**: केवल ADX > 25 (मजबूत ट्रेंड)
* **MACD Bullish Crossover**
* **Price within 5–10% of 52-week High**
* **Volatility (ATR %)**
* **Sector Relative Strength**
* **Automatic Buy Rating (0–100)**

इन सभी फ़िल्टरों के साथ आपका स्कैनर लगभग **institutional-quality momentum breakout screener** बन जाएगा और केवल उच्च-गुणवत्ता वाले ब्रेकआउट स्टॉक्स को शॉर्टलिस्ट करेगा।