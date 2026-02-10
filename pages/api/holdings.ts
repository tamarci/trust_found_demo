import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'
import Papa from 'papaparse'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    // Read CSV files
    const holdingsPath = path.join(process.cwd(), 'app', 'data', 'holdings.csv')
    const holdingsData = fs.readFileSync(holdingsPath, 'utf8')
    
    // Parse CSV
    const parsed = Papa.parse(holdingsData, { header: true, skipEmptyLines: true })
    const holdings = parsed.data

    // Calculate total value
    const totalValue = holdings.reduce((sum: number, h: any) => 
      sum + (parseFloat(h.valuation_current) || 0), 0
    )

    res.status(200).json({
      holdings,
      totalValue,
      count: holdings.length
    })
  } catch (error) {
    console.error('API Error:', error)
    res.status(500).json({ 
      error: 'Failed to load holdings data',
      holdings: [],
      totalValue: 0,
      count: 0
    })
  }
}
