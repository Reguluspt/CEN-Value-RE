import { useState, useEffect } from 'react';
import { Row, Col, Alert, Card, Skeleton } from 'antd';
import { useDashboard } from '../hooks/useDashboard';
import DashboardFilters from '../components/dashboard/DashboardFilters';
import KpiCards from '../components/dashboard/KpiCards';
import RevenueChart from '../components/dashboard/RevenueChart';
import MonthlySummaryTable from '../components/dashboard/MonthlySummaryTable';
import BankRevenueDonut from '../components/dashboard/BankRevenueDonut';
import CollectionStatusDonut from '../components/dashboard/CollectionStatusDonut';
import UnpaidCasesTable from '../components/dashboard/UnpaidCasesTable';

const now = new Date();
const currentMonth = `${String(now.getMonth() + 1).padStart(2, '0')}/${now.getFullYear()}`;

export default function Dashboard() {
  const [filters, setFilters] = useState({
    year: new Date().getFullYear().toString(),
    branch: '',
    customer_type: '',
    staff_name: '',
    status: '',
    month: currentMonth,
  });

  const { stats, filterOptions, isLoading, isError, error } = useDashboard(filters);

  // Sync selected target month when year changes or initial stats load
  useEffect(() => {
    if (filters.month && stats?.selected_month && filters.month !== stats.selected_month) {
      // The API selects the latest valid month after the year/filter options load.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFilters(prev => ({ ...prev, month: stats.selected_month }));
    }
  }, [filters.month, stats?.selected_month]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const monthOptions = stats?.available_months || [];
  const periodLabel = filters.month
    ? `tháng ${filters.month}`
    : `năm ${filters.year}`;
  const periodTitle = filters.month || `Năm ${filters.year}`;

  if (isLoading && !stats) {
    return (
      <div style={{ padding: '0 0 24px 0' }}>
        {/* Filter Bar Skeleton */}
        <Card style={{ marginBottom: 20, borderRadius: 12 }}>
          <Skeleton.Input active style={{ width: '100%' }} />
        </Card>
        {/* KPI Cards Skeleton */}
        <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
          {[1, 2, 3, 4].map(i => (
            <Col key={i} xs={24} sm={12} md={6}>
              <Card style={{ borderRadius: 12, border: '1px solid #d8e7e5' }}>
                <Skeleton active paragraph={{ rows: 2 }} />
              </Card>
            </Col>
          ))}
        </Row>
        {/* Charts Skeleton */}
        <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
          <Col xs={24} lg={12}>
            <Card style={{ borderRadius: 12, border: '1px solid #d8e7e5' }}>
              <Skeleton active paragraph={{ rows: 6 }} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card style={{ borderRadius: 12, border: '1px solid #d8e7e5' }}>
              <Skeleton active paragraph={{ rows: 6 }} />
            </Card>
          </Col>
        </Row>
      </div>
    );
  }

  if (isError) {
    return (
      <Alert
        message="Lỗi tải dữ liệu"
        description={error?.message || "Đã xảy ra lỗi khi kết nối đến server."}
        type="error"
        showIcon
        style={{ margin: 20 }}
      />
    );
  }

  return (
    <div style={{ padding: '0 0 24px 0' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <h1 style={{ fontSize: 32, fontWeight: 760, color: '#0f172a', margin: 0 }}>Dashboard</h1>
        <svg style={{ width: 20, height: 20, color: '#94a3b8', cursor: 'pointer' }} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
        </svg>
      </div>
      <div style={{ fontSize: 13, color: '#64748b', marginBottom: 20 }}>
        Theo dõi doanh thu dự kiến, thanh toán, công nợ và tỷ lệ doanh thu theo hệ thống ngân hàng.
      </div>

      {/* Filters Bar */}
      <DashboardFilters 
        filterOptions={filterOptions} 
        filters={filters} 
        onFilterChange={handleFilterChange} 
        monthOptions={monthOptions}
      />

      {/* KPI Cards */}
      <KpiCards stats={stats} periodLabel={periodLabel} />

      {/* Charts & Summary Table Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={12}>
          <RevenueChart
            data={filters.month ? stats?.daily_revenue || [] : stats?.monthly_revenue || []}
            granularity={filters.month ? 'day' : 'month'}
            selectedMonth={filters.month}
          />
        </Col>
        <Col xs={24} lg={12}>
          <MonthlySummaryTable data={stats?.monthly_revenue || []} />
        </Col>
      </Row>

      {/* Financial structure charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} lg={12}>
          <BankRevenueDonut
            data={stats?.bank_revenue || []}
            periodLabel={periodLabel}
          />
        </Col>
        <Col xs={24} lg={12}>
          <CollectionStatusDonut
            paid={stats?.year_paid || 0}
            unpaid={stats?.year_unpaid || 0}
            periodLabel={periodLabel}
          />
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <UnpaidCasesTable 
            data={stats?.unpaid_cases || []} 
            unpaidTotal={stats?.unpaid_total || 0}
            unpaidCount={stats?.unpaid_count || 0}
            periodLabel={periodTitle}
          />
        </Col>
      </Row>
    </div>
  );
}
