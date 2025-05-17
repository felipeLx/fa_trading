def calculate_forward_pe(forward_pe):
    """Analyze the Forward P/E ratio."""
    if forward_pe < 10:
        return "Undervalued"
    elif forward_pe > 20:
        return "Overvalued"
    return "Fairly Valued"

def analyze_profit_margins(profit_margins):
    """Analyze profit margins."""
    if profit_margins > 0.2:
        return "High Profitability"
    elif profit_margins > 0.1:
        return "Moderate Profitability"
    return "Low Profitability"

def evaluate_beta(beta):
    """Evaluate the risk based on beta."""
    if beta is None:
        return "Unknown Risk"
    if beta < 1:
        return "Low Risk"
    elif beta > 1.5:
        return "High Risk"
    return "Moderate Risk"

def calculate_dividend_yield(last_dividend_value, current_price):
    """Calculate the dividend yield."""
    if current_price == 0:
        return "Invalid Price"
    return (last_dividend_value / current_price) * 100

def analyze_peg_ratio(peg_ratio):
    """Analyze the PEG ratio."""
    if peg_ratio is None:
        return "Unknown PEG Ratio"
    if peg_ratio < 1:
        return "Undervalued Growth"
    elif peg_ratio > 2:
        return "Overvalued Growth"
    return "Fairly Valued Growth"

def analyze_asset(default_key_statistics, current_price):
    """Perform a comprehensive analysis of the asset."""
    analysis = {
        "forward_pe": calculate_forward_pe(default_key_statistics.get("forwardPE")),
        "profit_margins": analyze_profit_margins(default_key_statistics.get("profitMargins")),
        "beta": evaluate_beta(default_key_statistics.get("beta")),
        "dividend_yield": calculate_dividend_yield(default_key_statistics.get("lastDividendValue"), current_price),
        "peg_ratio": analyze_peg_ratio(default_key_statistics.get("pegRatio"))
    }
    return analysis

