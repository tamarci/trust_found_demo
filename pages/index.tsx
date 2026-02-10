import { useState, useEffect } from 'react'
import Head from 'next/head'
import dynamic from 'next/dynamic'

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

export default function Home() {
  const [activeTab, setActiveTab] = useState('summary')
  const [currency, setCurrency] = useState('EUR')
  const [language, setLanguage] = useState('en')
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load data from API
    fetch('/api/holdings')
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load data:', err)
        setLoading(false)
      })
  }, [])

  const currencySymbols = {
    EUR: '€',
    USD: '$',
    HUF: 'Ft'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>SQN Trust | Portfolio Dashboard</title>
        <meta name="description" content="Premium wealth management dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div>
                <h1 className="text-2xl font-bold text-primary">🏦 SQN Trust</h1>
                <p className="text-sm text-gray-600">Portfolio Dashboard</p>
              </div>
              <div className="flex gap-4 items-center">
                {/* Language Toggle */}
                <div className="flex gap-2">
                  <button
                    onClick={() => setLanguage('en')}
                    className={`px-3 py-1 rounded ${
                      language === 'en'
                        ? 'bg-primary text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    🇬🇧 EN
                  </button>
                  <button
                    onClick={() => setLanguage('hu')}
                    className={`px-3 py-1 rounded ${
                      language === 'hu'
                        ? 'bg-primary text-white'
                        : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    🇭🇺 HU
                  </button>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Currency Selector */}
          <div className="mb-6 flex gap-2">
            {['EUR', 'USD', 'HUF'].map((curr) => (
              <button
                key={curr}
                onClick={() => setCurrency(curr as any)}
                className={`px-4 py-2 rounded-lg ${
                  currency === curr
                    ? 'bg-primary text-white'
                    : 'bg-white text-gray-700 border border-gray-300'
                }`}
              >
                {curr}
              </button>
            ))}
          </div>

          {/* Tabs */}
          <div className="mb-6 border-b border-gray-200">
            <div className="flex gap-4 overflow-x-auto">
              {[
                { id: 'summary', label: '📊 Summary' },
                { id: 'assets', label: '💼 Assets' },
                { id: 'insights', label: '💡 Insights' },
                { id: 'reports', label: '📈 Reports' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 font-medium whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'text-primary border-b-2 border-primary'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            {activeTab === 'summary' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Portfolio Summary</h2>
                
                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Total Value</p>
                    <p className="text-2xl font-bold text-primary">
                      {currencySymbols[currency]}
                      {data?.totalValue?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">1Y Return</p>
                    <p className="text-2xl font-bold text-green-600">
                      +8.5%
                    </p>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">YTD Return</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      +5.2%
                    </p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Volatility</p>
                    <p className="text-2xl font-bold text-purple-600">
                      12.3%
                    </p>
                  </div>
                </div>

                {/* Charts would go here */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-4 h-64 flex items-center justify-center">
                    <p className="text-gray-500">Asset Allocation Chart</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 h-64 flex items-center justify-center">
                    <p className="text-gray-500">Performance Chart</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'assets' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Assets Overview</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {data?.holdings?.slice(0, 10).map((holding: any, idx: number) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {holding.asset_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {holding.asset_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {currencySymbols[currency]}{holding.valuation_current?.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'insights' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Portfolio Insights</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-bold mb-2">Diversification</h3>
                    <p className="text-sm text-gray-600">
                      Your portfolio is well-diversified across asset classes.
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <h3 className="font-bold mb-2">Performance</h3>
                    <p className="text-sm text-gray-600">
                      Above-market returns with controlled risk.
                    </p>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <h3 className="font-bold mb-2">Risk Level</h3>
                    <p className="text-sm text-gray-600">
                      Moderate risk profile aligned with objectives.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'reports' && (
              <div>
                <h2 className="text-2xl font-bold mb-6">Reports & Export</h2>
                <div className="space-y-4">
                  <button className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-opacity-90">
                    📥 Download CSV Report
                  </button>
                  <button className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg ml-4" disabled>
                    📄 Generate PDF (Coming Soon)
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-600">
              SQN Trust Portfolio Dashboard | Demo Version
            </p>
          </div>
        </footer>
      </main>
    </>
  )
}
