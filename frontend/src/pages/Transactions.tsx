import React, { useEffect, useState } from 'react';
import { getTransactions } from '../services/api';
import { Transaction } from '../types';
import { ListFilter, Search, Download } from 'lucide-react';

export const Transactions: React.FC = () => {
  const [txs, setTxs] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTxid, setSearchTxid] = useState('');
  const [searchWallet, setSearchWallet] = useState('');

  const fetchTxs = async () => {
    setLoading(true);
    try {
      const data = await getTransactions({
        limit: 100,
        txid: searchTxid || undefined,
        wallet: searchWallet || undefined,
      });
      setTxs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTxs();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
            <ListFilter className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            Transaction Explorer
          </h2>
          <p className="text-xs text-content-500 mt-1">
            Browse and filter ingested blockchain transactions and correlated network observations.
          </p>
        </div>
        <a
          href="http://127.0.0.1:8000/api/export/transactions/csv"
          target="_blank"
          rel="noreferrer"
          className="px-3.5 py-2 bg-surface-200 hover:bg-surface-300 text-brand-900 dark:text-brand-100 text-xs font-medium rounded-lg transition-all flex items-center gap-2 border border-surface-400"
        >
          <Download className="w-3.5 h-3.5" /> Export CSV
        </a>
      </div>

      {/* Filter Bar */}
      <div className="bg-surface-100 border border-surface-300 p-4 rounded-xl flex flex-wrap items-center gap-3">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-content-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by TXID..."
            value={searchTxid}
            onChange={(e) => setSearchTxid(e.target.value)}
            className="w-full bg-surface-50 border border-surface-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-brand-900 dark:text-brand-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
        <div className="flex-1 min-w-[200px] relative">
          <Search className="w-4 h-4 text-content-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by Wallet Address..."
            value={searchWallet}
            onChange={(e) => setSearchWallet(e.target.value)}
            className="w-full bg-surface-50 border border-surface-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-brand-900 dark:text-brand-100 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
        <button
          onClick={fetchTxs}
          className="px-4 py-1.5 bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium rounded-lg transition-all"
        >
          Apply Filters
        </button>
      </div>

      {/* Transactions Table */}
      <div className="bg-surface-100 border border-surface-300 rounded-xl shadow-lg flex flex-col">
        <div className="overflow-x-auto overflow-y-auto max-h-[650px] rounded-xl custom-scrollbar">
          <table className="w-full text-left text-xs text-content-600 relative">
            <thead className="sticky top-0 z-10 bg-surface-50/95 backdrop-blur font-mono text-[10px] text-content-500 uppercase border-b border-surface-300 shadow-sm">
              <tr>
                <th className="py-3 px-4 font-semibold tracking-wider">TXID</th>
                <th className="py-3 px-4 font-semibold tracking-wider">Timestamp</th>
                <th className="py-3 px-4 font-semibold tracking-wider">Source IP</th>
                <th className="py-3 px-4 font-semibold tracking-wider">Input Wallet</th>
                <th className="py-3 px-4 font-semibold tracking-wider">Output Wallet</th>
                <th className="py-3 px-4 text-right font-semibold tracking-wider">Amount (BTC)</th>
                <th className="py-3 px-4 text-right font-semibold tracking-wider">Fee (BTC)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200/50 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-content-400">
                    <div className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></span>
                      Loading transactions...
                    </div>
                  </td>
                </tr>
              ) : txs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-content-400">
                    No transactions found.
                  </td>
                </tr>
              ) : (
                txs.map((tx) => (
                  <tr key={tx.txid} className="hover:bg-surface-50 transition-colors group">
                    <td className="py-2.5 px-4 text-brand-600 dark:text-brand-400 font-semibold truncate max-w-[120px] group-hover:text-brand-500 transition-colors" title={tx.txid}>
                      {tx.txid}
                    </td>
                    <td className="py-2.5 px-4 text-content-500">{tx.timestamp || 'N/A'}</td>
                    <td className="py-2.5 px-4 text-content-600">{tx.src_ip || 'UNKNOWN'}</td>
                    <td className="py-2.5 px-4 text-content-600 truncate max-w-[140px]" title={tx.input_wallet}>
                      {tx.input_wallet || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-content-600 truncate max-w-[140px]" title={tx.output_wallet}>
                      {tx.output_wallet || 'N/A'}
                    </td>
                    <td className="py-2.5 px-4 text-right font-semibold text-verified-600">
                      {(tx.amount_btc ?? 0).toFixed(6)}
                    </td>
                    <td className="py-2.5 px-4 text-right text-content-500">
                      {(tx.fee_btc ?? 0).toFixed(6)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
