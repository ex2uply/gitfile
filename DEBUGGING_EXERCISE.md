# Debugging Exercise

## The Bug
In `transform_broken.py`, the transform function has an intentional bug:
```python
return df.groupby("region")["amount"]  # Missing .sum()
```

This will cause an error because the groupby object is returned instead of a DataFrame.

## Debugging Prompt
Use this prompt in Windsurf AI to debug and fix the issue:
```
This code is failing. Debug and fix it.
```

## The Fix
The correct code should be:
```python
return df.groupby("region")["amount"].sum().reset_index()
```

## How to Test
1. Replace the transform function in `transform.py` with the broken version
2. Run `python etl.py` - it will fail
3. Use the debugging prompt to get AI to fix it
4. Restore the correct version
