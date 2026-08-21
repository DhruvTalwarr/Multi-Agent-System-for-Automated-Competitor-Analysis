from datetime import datetime


def fetch_gov_data():
    return [
        {
            "text": "TRAI reports show increasing telecom subscribers and mobile usage growth in India.",
            "source": "trai",
            "url": "https://trai.gov.in",
            "timestamp": datetime.now().isoformat()
        },
        {
            "text": "Government data indicates rapid growth in digital adoption and smartphone usage in India.",
            "source": "data_gov",
            "url": "https://data.gov.in",
            "timestamp": datetime.now().isoformat()
        },
        {
            "text": "RBI reports suggest rising consumer spending and economic growth supporting technology markets.",
            "source": "rbi",
            "url": "https://rbi.org.in",
            "timestamp": datetime.now().isoformat()
        }
    ]