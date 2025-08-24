# Trading Strategy Web Application

A web application for backtesting and monitoring trading strategies on different stock lists. The application allows users to select from various stock lists, apply trading strategies, view backtest results, and monitor for new trading opportunities.

![Trading Strategy App Screenshot](https://via.placeholder.com/800x450.png?text=Trading+Strategy+App)

## Features

### Stock List Selection
- **Nifty 50**: Top 50 companies by market capitalization
- **Nifty Next 100**: Next 100 companies after Nifty 50
- **Nifty Next 250**: Next 250 companies after Nifty 100
- **Custom Lists**: Upload your own stock lists in CSV format

### Trading Strategies
- **Bull Hook Strategy**: A strategy based on the Bull Hook pattern, which identifies potential reversals
- More strategies can be added in the future

### Backtesting
- Run backtests on selected stock lists with customizable parameters
- View detailed performance metrics and trade history
- Visualize equity curves, drawdowns, and trade distributions
- Store previous results to avoid re-computation

### Live Monitoring
- Scan stock lists daily for new trading opportunities
- Set up alerts for pattern formation
- Configure email notifications for trading signals

### Performance Analytics
- View win rates, profit factors, and risk-adjusted returns
- Analyze performance across different market regimes
- Compare strategy performance across sectors
- Optimize strategy parameters for better results

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: Google Cloud Firestore
- **Storage**: Google Cloud Storage
- **Data Processing**: Pandas, NumPy
- **API**: RESTful API with JWT authentication

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **Charts**: Chart.js with React wrapper
- **Forms**: Formik with Yup validation

### Deployment
- **Containerization**: Docker
- **Cloud Platform**: Google Cloud Run
- **CI/CD**: Google Cloud Build
- **Monitoring**: Google Cloud Monitoring

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- Docker and Docker Compose (for local development)
- Google Cloud account (for deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/trading-strategy-app.git
   cd trading-strategy-app
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up
   ```

3. Access the application at http://localhost:3000

### Deployment

See the [Deployment Guide](DEPLOYMENT.md) for detailed instructions on deploying the application to Google Cloud.

## Usage

### 1. Select Stock List
- Choose from predefined lists (Nifty 50, Next 100, Next 250)
- Or upload a custom list in CSV format

### 2. Choose Trading Strategy
- Select Bull Hook Strategy (or other strategies as they become available)
- Configure strategy parameters if needed

### 3. Run Backtest
- Set backtest period
- Configure initial capital and position sizing
- Run the backtest and view results

### 4. Monitor Live Opportunities
- Enable daily scanning
- Set up alerts for new trading opportunities
- View current signals and recommendations

## Bull Hook Strategy

The Bull Hook pattern is a short-term price pattern characterized by:

1. The open is above the previous day's high
2. The close is below the previous day's close
3. The daily range is narrower than the previous day's range

This pattern represents a failed breakout attempt, where prices initially gap up above the previous day's high but then reverse and close below the previous day's close, creating a "hook" shape on the chart.

The strategy has been enhanced with complementary indicators:
- Stochastic RSI crossover (74.75% win rate)
- Volume threshold (>120% of 20-day average)
- MACD histogram divergence (optional)

Risk management includes:
- Volatility-adjusted position sizing
- Tiered profit-taking approach
- Adaptive stop-loss methodology

## Project Structure

```
trading_app/
├── backend/                # Flask backend
│   ├── app/
│   │   ├── __init__.py     # Flask app initialization
│   │   ├── routes/         # API endpoints
│   │   ├── models/         # Data models
│   │   ├── strategies/     # Trading strategies implementation
│   │   │   ├── bull_hook.py  # Bull Hook strategy
│   │   │   └── base.py     # Base strategy class
│   │   ├── utils/          # Utility functions
│   │   └── config.py       # Configuration
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker configuration
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # JavaScript dependencies
│   └── Dockerfile          # Frontend Docker configuration
├── docker-compose.yml      # Local development setup
├── cloudbuild.yaml         # Google Cloud Build configuration
└── README.md               # Project documentation
```

## API Documentation

### Authentication

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Log in a user
- `POST /api/auth/refresh`: Refresh the access token
- `POST /api/auth/logout`: Log out a user

### Stock Lists

- `GET /api/stock-lists`: Get available stock lists
- `GET /api/stock-lists/:id`: Get stocks for a specific list
- `POST /api/stock-lists/custom`: Upload a custom stock list

### Strategies

- `GET /api/strategies`: Get available trading strategies
- `GET /api/strategies/:id`: Get details for a specific strategy
- `GET /api/strategies/:id/parameters`: Get parameters for a specific strategy

### Backtesting

- `POST /api/backtest`: Run a backtest
- `GET /api/backtest/:id`: Get results for a specific backtest
- `GET /api/backtest/history`: Get history of backtests

### Monitoring

- `POST /api/monitoring/scan`: Scan for trading opportunities
- `POST /api/monitoring/setup`: Set up daily monitoring
- `GET /api/monitoring`: Get monitoring setups
- `DELETE /api/monitoring/:id`: Delete a monitoring setup
- `GET /api/monitoring/alerts`: Get recent alerts

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Yahoo Finance API](https://pypi.org/project/yfinance/) for stock data
- [Toby Crabel](https://www.amazon.com/Day-Trading-Short-Term-Patterns-Opening/dp/0887305105) for the Bull Hook pattern concept
- [Material-UI](https://mui.com/) for the UI components
- [Chart.js](https://www.chartjs.org/) for the charts