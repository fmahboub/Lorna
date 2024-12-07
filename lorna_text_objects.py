# FOR THE LANDING PAGE
# Define the dictionary with HTML content for centering
landing_content_dict = {
    "Why Lorna?": """
    <div style='text-align: center;'>
    <p>The <strong>Cash Flow Momentum Score (CFMS)</strong> simplifies investment decisions by focusing on what really matters:</p>
    <ul style="list-style-position: inside; padding-left: 0; text-align: left; display: inline-block;">
        <li><strong>Real Money Insights</strong>: Evaluates genuine cash flow over superficial profits.</li>
        <li><strong>Clear Scoring System</strong>: Condenses complex data into an easy-to-use score.</li>
        <li><strong>Future-Focused</strong>: Identifies companies with strong long-term potential.</li>
        <li><strong>Risk Reduction</strong>: Flags businesses with poor cash management or misleading numbers.</li>
    </ul>
    </div>
    """,
    'CFMS Explained': """
    <div style='text-align: center;'>
    <p>Our Cash Flow Momentum Score (CFMS) evaluates companies using five key metrics:</p>
    <table style='margin-left:auto;margin-right:auto;'>
        <tr><th><strong>Metric</strong></th><th><strong>Why It Matters</strong></th></tr>
        <tr><td><strong>Cash Flow Efficiency (CFE)</strong></td><td>Detects earnings backed by real cash flow.</td></tr>
        <tr><td><strong>EBITDA Margin</strong></td><td>Assesses core profitability and efficiency.</td></tr>
        <tr><td><strong>Operating Cash Flow Growth (OCFG)</strong></td><td>Indicates consistent operational scaling.</td></tr>
        <tr><td><strong>Free Cash Flow Yield (FCF Yield)</strong></td><td>Reflects shareholder cash returns.</td></tr>
        <tr><td><strong>Return on Invested Capital (ROIC)</strong></td><td>Highlights efficient capital usage.</td></tr>
    </table>
    <p>CFMS combines these metrics into a single score for easy comparison of cash flow strength.</p>
    </div>
    """,
    'Methodology': """
    <div style='text-align: center;'>
    <h3>How Does Lorna Work?</h3>
    <ul style="list-style-position: inside; padding-left: 0; text-align: left; display: inline-block;">
        <li><strong>Data Collection</strong>: Direct from financial reports for accuracy.</li>
        <li><strong>Normalization</strong>: Scores ranked on a percentile scale for fair comparison across all stocks, ensuring performance is evaluated against the best opportunities.</li>
        <li><strong>Weighted Scoring</strong>: Key metrics are weighted for a balanced CFMS score.</li>
        <li><strong>Final Scoring</strong>: High CFMS = Strong cash flow and operational excellence.</li>
    </ul>
    </div>
    """,
    'Time Periods': """
    <div style='text-align: center;'>
    <h3>Track Performance Over Time</h3>
    <p>Lorna provides insights for multiple timeframes:</p>
    <ul style="list-style-position: inside; padding-left: 0; text-align: left; display: inline-block;">
        <li><strong>Trailing Twelve Months (TTM)</strong>: Long-term cash flow trends.</li>
        <li><strong>Latest Quarter</strong>: Recent financial health.</li>
        <li><strong>Historical Tracking</strong>: Compare up to 5 prior quarters.</li>
    </ul>
    </div>
    """
}



# FOR THE TERMINOLOGY PAGE
# Combined metrics data, merging Normalized Scores
metrics_data = [
    {
        "Metric":"Cash Flow Momentum Score (CFMS)",
        "Definition": "A score that measures how well a company generates, grows, and uses its cash.",
        "Rationale": "Simplifies financial data into an easy-to-understand score, helping investors pick strong companies.",
        "Description": "Evaluates companies using five key metrics. Normalized scores range from 1-100, with higher scores indicating better cash flow health."

    },
    {
        "Metric": "Cash Flow Efficiency (CFE)",
        "Definition": "Measures the proportion of net income that is converted into cash from operating activities.",
        "Rationale": "A ratio above 1 indicates high earnings quality, suggesting that net income is backed by actual cash flow.",
        "Description": "Reflects the quality of earnings by showing how well net income translates into real cash flow. Normalized scores range from 1-100, with higher scores indicating better earnings quality."
    },
    {
        "Metric": "EBITDA Margin",
        "Definition": "The ratio of Earnings Before Interest, Taxes, Depreciation, and Amortization (EBITDA) to revenue.",
        "Rationale": "Evaluates core profitability and operational efficiency, focusing on a company's ability to generate cash from its operations.",
        "Description": "Indicates how efficiently a company generates profit from its core operations. Normalized scores range from 1-100, with higher scores reflecting stronger EBITDA margins."
    },
    {
        "Metric": "Operating Cash Flow Growth (OCFG)",
        "Definition": "The year-over-year growth rate of operating cash flow.",
        "Rationale": "Sustained growth in OCF indicates that a company is successfully expanding its business and generating more cash from core operations.",
        "Description": "Highlights the company's ability to grow its cash generation over time. Normalized scores range from 1-100, with higher scores showing robust and sustained growth."
    },
    {
        "Metric": "Free Cash Flow Yield (FCF Yield)",
        "Definition": "The ratio of free cash flow to market capitalization.",
        "Rationale": "Reflects how much cash a company is generating relative to its stock price, serving as an indicator of valuation and shareholder returns.",
        "Description": "Helps investors assess the stock's value relative to its cash-generating capacity. Normalized scores range from 1-100, with higher scores indicating better valuation efficiency."
    },
    {
        "Metric": "Return on Invested Capital (ROIC)",
        "Definition": "Measures how efficiently a company generates profits relative to the capital it has invested in its business.",
        "Rationale": "A high ROIC indicates efficient use of capital, suggesting strong value creation for shareholders.",
        "Description": "Shows how well a company uses its resources to create value. Normalized scores range from 1-100, with higher scores reflecting more efficient capital use."
    }
]