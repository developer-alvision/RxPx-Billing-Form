# RxPx-Billing-Form

Billing form for RxPx Hospitals. Choose **Pharmacy bill** or **Lab bill**, fill in the patient and items, then print the bill or open it as a filled PDF. It is a single HTML file that works offline on a computer or a phone.

## Use it

Open `index.html` in Chrome, or upload it to any web host (no server code needed).

1. Choose **Pharmacy bill** or **Lab bill**.
2. Fill in the patient, bill number and items. Amounts (quantity × unit price) and the total add up by themselves.
3. Tap **Open PDF** to go to the filled PDF, or **Print bill** to print straight away. Print on A4 at 100% scale.

Patient details stay when you switch between the two bills. After a bill is printed or saved, the next bill number is suggested. Nothing you type is uploaded; only the last bill number of each type is kept in the browser.

## What's in the repo

| Path | What it is |
| --- | --- |
| `index.html` | The finished app: open or host this file |
| `src/app.html` | Source of the page: form, styles and script |
| `templates/` | The two bill PDFs |
| `assets/` | Drawings of the blank bills and the logo, used for the preview and printing |
| `tools/` | Scripts that remake `assets/` and build `index.html` |

## How it works

- The fill-in fields in the template PDFs (`Patient_Name`, `Age`, `Gender`, `Phone_Number`, `Bill_No`, `Date_Time`, `Item_1_Description` … `Item_8_Amount`, `Total_Amount`) set where each value goes, its font size and its character limit.
- **Open PDF** and **Save as PDF** copy the bill page into a new PDF and write the values at those field positions with [pdf-lib](https://github.com/Hopding/pdf-lib). The page is copied rather than re-saved because the template PDFs contain an edit history that pdf-lib cannot re-save correctly.
- The on-screen preview and **Print bill** use a drawing of the blank bill with the same values laid on top, so the screen, the printout and the PDF match.
- The lab bill has no amount column, so a test's amount (if given) prints at the right of its row.

## Change a bill

Edit the PDF in `templates/`, keeping the field names, then rebuild:

```
npm install                      # gets pdf-lib
pip install pillow pdfplumber    # make_assets also needs Poppler (pdftocairo, pdfimages)
npm run assets                   # remakes assets/ from the PDFs
npm run build                    # writes index.html
```

To change the form itself, edit `src/app.html` and run `npm run build`.
