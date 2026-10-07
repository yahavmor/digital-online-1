# B-roll library
Drop cutaway clips here. Name them by what they show — `money_cash_01.mp4`, `laptop_typing.mov`,
`כסף_שטרות.mp4` — or tag them in `index.yaml`:

```yaml
city_night_4k.mp4: [success, עיר, לילה]
```
The factory matches clip names/tags against spoken keywords and inserts matches automatically.
Unmatched opportunities (with suggested stock-search queries) are listed in each job's
`project/*.timeline.json → broll`.
