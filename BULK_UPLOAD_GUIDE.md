# SORA Warehouse Bulk Upload Feature

## Overview
The Bulk Upload feature allows you to process multiple inventory transactions at once using CSV files. This is perfect for handling large batches of data efficiently.

## Features

### 1. **Duplicate Detection**
- Automatically detects entries that have already been processed
- Uses SHA-256 hash-based tracking to identify duplicates
- Shows clear distinction between new and duplicate entries

### 2. **Visual Feedback**
- Real-time statistics showing:
  - Total entries in your CSV
  - Number of new entries (ready to save)
  - Number of duplicate entries (already processed)
- Color-coded table rows:
  - **Green badge**: New entries ready to be saved
  - **Yellow badge**: Duplicate entries (will be skipped)

### 3. **Smart Processing**
- Handles both IN (add stock) and OUT (remove stock) operations
- Validates ID format (must be X, S, C, M, A, or B followed by numbers)
- Processes multi-line entries in the "Answer in This format" column
- Preserves all other CSV columns (date, IN/OUT, TYPE, etc.)

## How to Use

### Step 1: Prepare Your CSV File
Your CSV should have these columns:
```
date, Select IN or OUT, Select TYPE, Answer in This format (ID-SIZE-QTY)
```

Example CSV format:
```csv
date,Select IN or OUT,Select TYPE,Answer in This format (ID-SIZE-QTY)
2024-01-15,IN,X,"X1-M-10
X2-L-15"
2024-01-15,IN,S,"S1-M-20
S2-S-25"
2024-01-16,OUT,C,"C1-M-5"
```

**Important Notes:**
- The "Answer in This format" column can contain multiple lines
- Each line should be formatted as: `ID-SIZE-QTY`
- Example: `X1-M-10` means ID=X1, Size=M, Quantity=10

### Step 2: Upload Your File
1. Log in to the SORA Warehouse interface
2. Click the "Bulk Upload" button
3. Either:
   - Click the upload area to browse for your file
   - Drag and drop your CSV file directly

### Step 3: Review the Results
After uploading, you'll see:
- **Statistics**: Total, new, and duplicate entries
- **Preview Table**: All entries with their status badges
- Duplicate entries are highlighted in yellow

### Step 4: Confirm & Save
1. Review the entries carefully
2. Click "Confirm & Save" to process all new entries
3. The system will:
   - Process IN entries (add stock)
   - Process OUT entries (remove stock)
   - Mark all successfully saved entries as processed
   - Show you a summary of saved vs failed entries

## File Structure

### Core Files
- **BulkFlow.py**: CSV processor that splits multi-line entries
- **BulkFlowFirewall.py**: Duplicate detection and tracking system
- **input_system.py**: Web interface and Flask routes

### Tracking File
- **bulk_flow_tracking.json**: Automatically created to store processed entry hashes
  - This file tracks what's been processed to prevent duplicates
  - Don't delete this file unless you want to reset tracking

## CSV Processing Details

### Input Format
The CSV processor looks for the column named "Answer in This format (ID-SIZE-QTY)" and splits it into individual entries.

**Before Processing:**
```
Answer in This format (ID-SIZE-QTY)
"X1-M-10
X2-L-15"
```

**After Processing:**
```
ID    Size    QTY
X1    M       10
X2    L       15
```

### Validation Rules
1. **ID Format**: Must match pattern `^[XSCMAB]\d+$`
   - Valid: X1, S12, C5, M23, A8, B100
   - Invalid: T1, XYZ, 123, X-1

2. **Action**: Must be either "IN" or "OUT"
   - IN: Adds stock to inventory
   - OUT: Removes stock from inventory

3. **Type**: Must match selected TYPE in your CSV
   - Valid types: X, S, C, M, A, B

4. **Size**: Any size format (S, M, L, XL, etc.)

5. **Quantity**: Must be a valid positive integer

## Error Handling

### Upload Errors
- **"No file uploaded"**: Make sure you selected a file
- **"No valid entries found"**: Check your CSV format
- **Processing errors**: Check the console for detailed error messages

### Save Errors
- **Invalid ID format**: Entry will be skipped with error message
- **Invalid action**: Must be IN or OUT
- **Insufficient stock**: OUT operations require enough stock available

The system will show you exactly which entries failed and why.

## Technical Details

### Duplicate Detection Algorithm
```python
# Creates unique hash for each entry
hash = SHA256(date|IN/OUT|TYPE|ID|Size|QTY)

# Example:
Entry: 2024-01-15|IN|X|X1|M|10
Hash: a1b2c3d4...
```

### Flask Routes
- **POST /bulk_upload**: Processes uploaded CSV file
- **POST /bulk_save**: Saves confirmed entries to database

### Database Operations
- IN operations: Call `warehouse.add_stock()`
- OUT operations: Call `warehouse.remove_stock()`
- All operations respect the security firewall (ID validation)

## Best Practices

1. **Test with Small Files First**: Start with 5-10 entries to verify format
2. **Check for Duplicates**: The system will catch them, but it's good to review
3. **Backup Your Data**: Export reports before large bulk uploads
4. **Review Before Saving**: Always check the preview table before confirming
5. **Keep Tracking File**: Don't delete `bulk_flow_tracking.json` unless intentional

## Troubleshooting

### Problem: All entries show as duplicates
**Solution**: If you want to reset tracking, delete `bulk_flow_tracking.json`

### Problem: Some entries fail to save
**Solution**: Check the error message for specific issues (invalid ID, insufficient stock, etc.)

### Problem: CSV not processing correctly
**Solution**: 
- Verify column names match exactly
- Check for extra spaces or special characters
- Ensure multi-line entries are properly quoted

### Problem: Upload button doesn't appear
**Solution**: Make sure you're logged in and the page has loaded completely

## Security Features

- All bulk upload routes require authentication
- Rate limiting applies to prevent abuse
- ID validation prevents invalid entries
- Session management ensures secure access

## Example Test File

Use `test_bulk_upload.csv` as a template:
```csv
date,Select IN or OUT,Select TYPE,Answer in This format (ID-SIZE-QTY)
2024-01-15,IN,X,"X1-M-10
X2-L-15"
2024-01-15,IN,S,"S1-M-20"
2024-01-16,OUT,C,"C1-M-5"
```

## Support

For issues or questions:
1. Check this documentation
2. Review the console for error messages
3. Verify your CSV format matches the examples
4. Test with the included `test_bulk_upload.csv` file
