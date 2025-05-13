import csv
from database import fetch_balance_sheet_data

def analyze_company_health_from_db(ticker):
    """Fetch financial data from the database and analyze company health."""
    data = fetch_balance_sheet_data(ticker)

    if not data:
        print(f"No financial data found for {ticker} in the database.")
        return None

    financial_ratios = {
        'current_ratio': data['current_ratio'],
        'debt_to_equity_ratio': data['debt_to_equity_ratio']
    }

    health_analysis = {
        'current_ratio': "Healthy" if financial_ratios['current_ratio'] >= 1.5 else "Unhealthy",
        'debt_to_equity_ratio': "Healthy" if financial_ratios['debt_to_equity_ratio'] <= 1.0 else "Unhealthy"
    }

    return {
        'ticker': ticker,
        'end_date': data['end_date'],
        'current_ratio': financial_ratios['current_ratio'],
        'debt_to_equity_ratio': financial_ratios['debt_to_equity_ratio'],
        'current_ratio_health': health_analysis['current_ratio'],
        'debt_to_equity_health': health_analysis['debt_to_equity_ratio']
    }

def save_analysis_to_csv(filename, analysis_results):
    """Save the analysis results to a CSV file, updating if it already exists."""
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=analysis_results[0].keys())

            # Write the header only if the file is empty
            if file.tell() == 0:
                writer.writeheader()

            writer.writerows(analysis_results)

        print(f"Analysis results saved to {filename}.")
    except Exception as e:
        print(f"Failed to save analysis results to CSV: {e}")

if __name__ == "__main__":
    tickers = ["PETR4", "VALE3", "ITUB4", "AMER3", "B3SA3", "MGLU3", "LREN3", "ITSA4", "BBAS3", "RENT3", "ABEV3"]
    analysis_results = []

    for ticker in tickers:
        print(f"Analyzing {ticker}...")
        result = analyze_company_health_from_db(ticker)
        if result:
            analysis_results.append(result)

    if analysis_results:
        save_analysis_to_csv("company_health_analysis.csv", analysis_results)
