import { useMemo, useState } from 'react';
import { AppShell } from '@astryxdesign/core/AppShell';
import { SideNav, SideNavItem, SideNavSection } from '@astryxdesign/core/SideNav';
import { Text } from '@astryxdesign/core/Text';
import { hasReBootstrap } from './localServiceClient';
import { displayPercentToFraction, fractionToDisplayPercent } from './percent';
import { workbenchApi } from './workbenchApi';
import './generated/astryx-core.scoped.css';
import './generated/neutral-theme.scoped.css';
import './astryx.css';

const PROFILE_ID = 'cenvalue-re-n08-0038-v1';
const PROFILE_VERSION = '1';
const FACTORS = Array.from({ length: 11 }, (_, index) => `C${index + 1}`);

const emptyComparable = (order) => ({
  order,
  legalAddress: '',
  currentAddress: '',
  askingPrice: '',
  negotiatedPrice: '',
  negotiationPercent: '',
  area: '',
  frontage: '',
  depth: '',
  shape: '',
  buildingArea: '',
  buildingRemainingQuality: '',
});

const emptyAdjustment = (order) => ({
  order,
  normalizedBase: '',
  evidenceRef: '',
  sourceRevision: '',
  rates: Object.fromEntries(FACTORS.map((key) => [key, ''])),
  currentRun: null,
});

function Field({ label, value, onChange, type = 'text', placeholder = '', disabled = false }) {
  return (
    <label className="cenvalue-re-field">
      <span>{label}</span>
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function ResultBox({ value, empty = 'Chưa có dữ liệu current.' }) {
  if (!value) {
    return <p className="cenvalue-re-muted">{empty}</p>;
  }
  return <pre className="cenvalue-re-result">{JSON.stringify(value, null, 2)}</pre>;
}

function ReShell() {
  const [caseId, setCaseId] = useState('');
  const [caseFields, setCaseFields] = useState({
    caseCode: '',
    appraisalDate: '',
    clientName: '',
    valuationPurpose: '',
  });
  const [subject, setSubject] = useState({
    legalAddress: '',
    currentAddress: '',
    province: '',
    latitude: '',
    longitude: '',
    parcelNumber: '',
    mapSheetNumber: '',
    totalArea: '',
    compliantArea: '',
    noncompliantArea: '',
    noncompliantUnitPrice: '',
    frontage: '',
    depth: '',
    shape: '',
  });
  const [comparables, setComparables] = useState([1, 2, 3].map(emptyComparable));
  const [adjustments, setAdjustments] = useState([1, 2, 3].map(emptyAdjustment));
  const [decisionActor, setDecisionActor] = useState('');
  const [quality, setQuality] = useState(null);
  const [indication, setIndication] = useState(null);
  const [indicationForm, setIndicationForm] = useState({
    selectionKind: 'COMPARABLE',
    selectedComparableOrder: '1',
    confirmedBy: '',
    reason: '',
  });
  const [construction, setConstruction] = useState({
    amount: '',
    evidenceRef: '',
    suppliedBy: '',
  });
  const [finalValuation, setFinalValuation] = useState(null);
  const [exportForm, setExportForm] = useState({ templatePath: '', outputPath: '' });
  const [exportArtifact, setExportArtifact] = useState(null);
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const themeMode =
    typeof document !== 'undefined' && document.documentElement.dataset.theme === 'dark'
      ? 'dark'
      : 'light';
  const bootstrapReady = hasReBootstrap();
  const activeCase = Boolean(caseId);

  const sideNav = (
    <SideNav>
      <SideNavSection title="CenValue RE">
        <SideNavItem label="Manual workbench" href="/re" isSelected />
        <SideNavItem label="Legacy dashboard" href="/dashboard" />
      </SideNavSection>
    </SideNav>
  );

  const updateComparable = (order, patch) => {
    setComparables((current) =>
      current.map((item) => (item.order === order ? { ...item, ...patch } : item)),
    );
  };

  const updateAdjustment = (order, patch) => {
    setAdjustments((current) =>
      current.map((item) => (item.order === order ? { ...item, ...patch } : item)),
    );
  };

  const run = async (successMessage, operation) => {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const result = await operation();
      setNotice(successMessage);
      return result;
    } catch (caught) {
      setError(`${caught.code ? `${caught.code}: ` : ''}${caught.message || String(caught)}`);
      return null;
    } finally {
      setBusy(false);
    }
  };

  const characteristicsByKey = (records = []) =>
    Object.fromEntries(
      records.map((item) => [
        item.definition_key,
        item.decimal_value ?? item.text_value ?? item.code_value ?? item.bool_value ?? item.date_value,
      ]),
    );

  const applySnapshot = (snapshot) => {
    if (!snapshot?.case) return;
    setCaseId(snapshot.case.id);
    setCaseFields({
      caseCode: snapshot.case.case_code || '',
      appraisalDate: snapshot.case.appraisal_date || '',
      clientName: snapshot.case.client_name || '',
      valuationPurpose: snapshot.case.valuation_purpose || '',
    });

    if (snapshot.subject) {
      const property = snapshot.subject.property;
      const parcel = snapshot.subject.parcels?.[0] || {};
      const components = snapshot.subject.land_valuation_components || [];
      const compliant = components.find(
        (item) => item.planning_status === 'COMPLIANT' && item.valuation_basis === 'MARKET_INDICATED',
      );
      const noncompliant = components.find((item) => item.planning_status === 'NON_COMPLIANT');
      const chars = characteristicsByKey(snapshot.subject.characteristics);
      setSubject({
        legalAddress: property.legal_address || '',
        currentAddress: property.current_address || '',
        province: chars['address.current.province'] || '',
        latitude: property.latitude || '',
        longitude: property.longitude || '',
        parcelNumber: parcel.parcel_number || '',
        mapSheetNumber: parcel.map_sheet_number || '',
        totalArea: parcel.total_area_m2 || '',
        compliantArea: compliant?.area_m2 || '',
        noncompliantArea: noncompliant?.area_m2 || '',
        noncompliantUnitPrice: noncompliant?.unit_price_vnd_per_m2 || '',
        frontage: chars.frontage || '',
        depth: chars.depth || '',
        shape: chars.shape || '',
      });
    }

    const restored = [1, 2, 3].map((order) => {
      const bundle = snapshot.comparables?.find((item) => item.property.comparable_order === order);
      if (!bundle) return emptyComparable(order);
      const chars = characteristicsByKey(bundle.characteristics);
      const observation = bundle.market_observation || {};
      return {
        order,
        legalAddress: bundle.property.legal_address || '',
        currentAddress: bundle.property.current_address || '',
        askingPrice: observation.asking_or_sale_price_vnd || '',
        negotiatedPrice: observation.negotiated_price_vnd || '',
        negotiationPercent: fractionToDisplayPercent(observation.negotiation_rate_pct),
        area: chars.area_m2 || '',
        frontage: chars.frontage || '',
        depth: chars.depth || '',
        shape: chars.shape || '',
        buildingArea: chars.building_area_m2 || '',
        buildingRemainingQuality: chars.building_remaining_quality || '',
      };
    });
    setComparables(restored);
  };

  const resumeDownstream = async (id) => {
    const adjustmentResults = await Promise.allSettled(
      [1, 2, 3].map((order) => workbenchApi.adjustmentState(id, order)),
    );
    setAdjustments(
      adjustmentResults.map((result, index) => {
        const order = index + 1;
        if (result.status !== 'fulfilled') return emptyAdjustment(order);
        const state = result.value;
        const rates = Object.fromEntries(FACTORS.map((key) => [key, '']));
        for (const decision of state.decisions || []) {
          rates[decision.factor_key] = decision.selected_explicitly
            ? fractionToDisplayPercent(decision.selected_rate_pct)
            : '';
        }
        return {
          order,
          normalizedBase: state.source_state?.normalized_base_price_vnd_per_m2 || '',
          evidenceRef: state.source_state?.normalized_base_evidence_ref || '',
          sourceRevision: state.source_state?.source_revision
            ? String(state.source_state.source_revision)
            : '',
          rates,
          currentRun: state.current_run,
        };
      }),
    );

    const [qualityResult, indicationResult, finalResult] = await Promise.allSettled([
      workbenchApi.quality(id),
      workbenchApi.currentIndication(id),
      workbenchApi.currentFinal(id),
    ]);
    setQuality(qualityResult.status === 'fulfilled' ? qualityResult.value : null);
    setIndication(indicationResult.status === 'fulfilled' ? indicationResult.value : null);
    setFinalValuation(finalResult.status === 'fulfilled' ? finalResult.value : null);
  };

  const createCase = () =>
    run('Đã tạo hồ sơ canonical.', async () => {
      const snapshot = await workbenchApi.createCase({
        case_code: caseFields.caseCode,
        appraisal_date: caseFields.appraisalDate,
        profile_id: PROFILE_ID,
        profile_version: PROFILE_VERSION,
        client_name: caseFields.clientName || null,
        valuation_purpose: caseFields.valuationPurpose || null,
      });
      applySnapshot(snapshot);
      return snapshot;
    });

  const resumeCase = () =>
    run('Đã khôi phục hồ sơ và current downstream evidence.', async () => {
      const snapshot = await workbenchApi.resumeCase(caseId);
      applySnapshot(snapshot);
      await resumeDownstream(snapshot.case.id);
      return snapshot;
    });

  const saveSubject = () =>
    run('Đã lưu TSTĐ.', async () => {
      const snapshot = await workbenchApi.saveSubject(caseId, {
        legal_address: subject.legalAddress,
        current_address: subject.currentAddress,
        legal_review_status: 'MANUAL_REVIEWED',
        latitude: subject.latitude || null,
        longitude: subject.longitude || null,
        parcels: [
          {
            parcel_number: subject.parcelNumber || null,
            map_sheet_number: subject.mapSheetNumber || null,
            total_area_m2: subject.totalArea,
            valuation_components: [
              {
                planning_status: 'COMPLIANT',
                area_m2: subject.compliantArea,
                valuation_basis: 'MARKET_INDICATED',
                include_in_final_value: true,
              },
              {
                planning_status: 'NON_COMPLIANT',
                area_m2: subject.noncompliantArea,
                valuation_basis: 'OFFICIAL_LAND_PRICE',
                include_in_final_value: true,
                unit_price_vnd_per_m2: subject.noncompliantUnitPrice,
                policy_version: 'MANUAL_WORKBENCH',
              },
            ],
          },
        ],
        characteristics: [
          { definition_key: 'address.current.province', text_value: subject.province },
          { definition_key: 'frontage', decimal_value: subject.frontage },
          { definition_key: 'depth', decimal_value: subject.depth },
          { definition_key: 'shape', text_value: subject.shape },
        ],
      });
      applySnapshot(snapshot);
      return snapshot;
    });

  const saveComparable = (item) =>
    run(`Đã lưu TSSS${String(item.order).padStart(2, '0')}.`, async () => {
      const fraction = displayPercentToFraction(item.negotiationPercent);
      const snapshot = await workbenchApi.saveComparable(caseId, item.order, {
        legal_address: item.legalAddress,
        current_address: item.currentAddress,
        completeness_status: 'COMPLETE',
        asking_or_sale_price_vnd: item.askingPrice,
        negotiated_price_vnd: item.negotiatedPrice,
        negotiation_rate_pct: fraction,
        characteristics: [
          { definition_key: 'area_m2', decimal_value: item.area },
          { definition_key: 'frontage', decimal_value: item.frontage },
          { definition_key: 'depth', decimal_value: item.depth },
          { definition_key: 'shape', text_value: item.shape },
          { definition_key: 'building_area_m2', decimal_value: item.buildingArea },
          {
            definition_key: 'building_remaining_quality',
            decimal_value: item.buildingRemainingQuality,
          },
        ],
      });
      applySnapshot(snapshot);
      return snapshot;
    });

  const bindBase = (item) =>
    run(`Đã bind P0 cho TSSS${String(item.order).padStart(2, '0')}.`, async () => {
      const state = await workbenchApi.bindAdjustmentBase(caseId, item.order, {
        normalized_base_price_vnd_per_m2: item.normalizedBase,
        evidence_ref: item.evidenceRef,
      });
      updateAdjustment(item.order, { sourceRevision: String(state.source_revision) });
      return state;
    });

  const saveRate = (item, factorKey) =>
    run(`Đã lưu ${factorKey} cho TSSS${String(item.order).padStart(2, '0')}.`, async () => {
      const selectedRate = displayPercentToFraction(item.rates[factorKey]);
      if (selectedRate === null) {
        throw new Error(`${factorKey} đang để trống; missing không được đổi thành 0%.`);
      }
      const decision = await workbenchApi.selectAdjustmentRate(caseId, item.order, factorKey, {
        selected_rate: selectedRate,
        selected_by: decisionActor,
        source_data_revision: item.sourceRevision || null,
      });
      return decision;
    });

  const runAdjustment = (item) =>
    run(`Đã chạy adjustment TSSS${String(item.order).padStart(2, '0')}.`, async () => {
      const result = await workbenchApi.runAdjustment(caseId, item.order, {
        source_data_revision: item.sourceRevision || null,
      });
      const state = await workbenchApi.adjustmentState(caseId, item.order);
      updateAdjustment(item.order, { currentRun: state.current_run });
      return result;
    });

  const previewQuality = () =>
    run('Đã đọc quality/readiness từ application.', async () => {
      const result = await workbenchApi.quality(caseId);
      setQuality(result);
      return result;
    });

  const confirmIndication = () =>
    run('Đã ghi nhận human indication.', async () => {
      const result = await workbenchApi.confirmIndication(caseId, {
        selection_kind: indicationForm.selectionKind,
        selected_comparable_order:
          indicationForm.selectionKind === 'COMPARABLE'
            ? Number(indicationForm.selectedComparableOrder)
            : null,
        confirmed_by: indicationForm.confirmedBy,
        reason: indicationForm.reason,
      });
      setIndication(result);
      return result;
    });

  const bindConstruction = () =>
    run('Đã bind supplied construction aggregate.', () =>
      workbenchApi.bindConstruction(caseId, {
        amount_vnd: construction.amount,
        evidence_ref: construction.evidenceRef,
        supplied_by: construction.suppliedBy,
      }),
    );

  const composeFinal = () =>
    run('Đã compose final valuation.', async () => {
      const result = await workbenchApi.composeFinal(caseId);
      setFinalValuation(result);
      return result;
    });

  const generateWorkbook = () =>
    run('Đã tạo workbook output; Excel qualification vẫn NOT_RUN.', async () => {
      const result = await workbenchApi.generateWorkbook(caseId, {
        template_path: exportForm.templatePath,
        output_path: exportForm.outputPath,
      });
      setExportArtifact(result);
      return result;
    });

  const completedRates = useMemo(
    () => adjustments.map((item) => FACTORS.filter((key) => item.rates[key] !== '').length),
    [adjustments],
  );

  return (
    <div
      className="cenvalue-re-surface"
      data-astryx-theme="neutral"
      data-theme={themeMode}
      data-re-workbench="e1-pr-006"
    >
      <AppShell contentPadding={0} sideNav={sideNav}>
        <main className="cenvalue-re-workbench">
          <header className="cenvalue-re-heading">
            <Text type="large">CenValue RE — Manual Walking Skeleton</Text>
            <Text type="body">
              Application-owned calculation · human-owned decisions · Excel as output compatibility.
            </Text>
            <div className={bootstrapReady ? 'cenvalue-re-status is-ready' : 'cenvalue-re-status'}>
              {bootstrapReady
                ? 'Local-service session: ready'
                : 'Local-service session: chưa được supervisor bootstrap — mọi action fail closed.'}
            </div>
            {notice ? <div className="cenvalue-re-notice">{notice}</div> : null}
            {error ? <div className="cenvalue-re-error" role="alert">{error}</div> : null}
          </header>

          <section className="cenvalue-re-panel" aria-labelledby="stage-case">
            <h2 id="stage-case">1. Hồ sơ — tạo / resume</h2>
            <div className="cenvalue-re-grid">
              <Field label="Case ID để resume" value={caseId} onChange={setCaseId} />
              <Field
                label="Mã hồ sơ"
                value={caseFields.caseCode}
                onChange={(value) => setCaseFields((current) => ({ ...current, caseCode: value }))}
              />
              <Field
                label="Ngày thẩm định"
                type="date"
                value={caseFields.appraisalDate}
                onChange={(value) => setCaseFields((current) => ({ ...current, appraisalDate: value }))}
              />
              <Field
                label="Khách hàng"
                value={caseFields.clientName}
                onChange={(value) => setCaseFields((current) => ({ ...current, clientName: value }))}
              />
              <Field
                label="Mục đích"
                value={caseFields.valuationPurpose}
                onChange={(value) => setCaseFields((current) => ({ ...current, valuationPurpose: value }))}
              />
              <Field label="Profile" value={`${PROFILE_ID}@${PROFILE_VERSION}`} onChange={() => {}} disabled />
            </div>
            <div className="cenvalue-re-actions">
              <button type="button" disabled={busy || !bootstrapReady} onClick={createCase}>Tạo hồ sơ</button>
              <button type="button" disabled={busy || !bootstrapReady || !caseId} onClick={resumeCase}>Resume</button>
            </div>
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-subject">
            <h2 id="stage-subject">2. TSTĐ — chủ thể / thửa đất</h2>
            <div className="cenvalue-re-grid">
              {[
                ['Địa chỉ pháp lý', 'legalAddress'],
                ['Địa chỉ hiện tại', 'currentAddress'],
                ['Tỉnh/TP', 'province'],
                ['Vĩ độ', 'latitude'],
                ['Kinh độ', 'longitude'],
                ['Số thửa', 'parcelNumber'],
                ['Tờ bản đồ', 'mapSheetNumber'],
                ['Tổng diện tích m²', 'totalArea'],
                ['Diện tích phù hợp m²', 'compliantArea'],
                ['Diện tích không phù hợp m²', 'noncompliantArea'],
                ['Đơn giá đất không phù hợp', 'noncompliantUnitPrice'],
                ['Mặt tiền', 'frontage'],
                ['Chiều sâu', 'depth'],
                ['Hình dạng', 'shape'],
              ].map(([label, key]) => (
                <Field
                  key={key}
                  label={label}
                  value={subject[key]}
                  onChange={(value) => setSubject((current) => ({ ...current, [key]: value }))}
                />
              ))}
            </div>
            <button type="button" disabled={busy || !activeCase} onClick={saveSubject}>Lưu TSTĐ</button>
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-comparables">
            <h2 id="stage-comparables">3. TSSS01 / TSSS02 / TSSS03</h2>
            <p className="cenvalue-re-muted">Tỷ lệ thương lượng hiển thị theo %, nhưng gửi canonical fraction bằng chuyển đổi chuỗi chính xác.</p>
            <div className="cenvalue-re-columns">
              {comparables.map((item) => (
                <article className="cenvalue-re-card" key={item.order}>
                  <h3>TSSS{String(item.order).padStart(2, '0')}</h3>
                  {[
                    ['Địa chỉ pháp lý', 'legalAddress'],
                    ['Địa chỉ hiện tại', 'currentAddress'],
                    ['Giá chào/bán', 'askingPrice'],
                    ['Giá thương lượng', 'negotiatedPrice'],
                    ['Tỷ lệ thương lượng (%)', 'negotiationPercent'],
                    ['Diện tích m²', 'area'],
                    ['Mặt tiền', 'frontage'],
                    ['Chiều sâu', 'depth'],
                    ['Hình dạng', 'shape'],
                    ['Diện tích xây dựng', 'buildingArea'],
                    ['Chất lượng còn lại (fraction)', 'buildingRemainingQuality'],
                  ].map(([label, key]) => (
                    <Field
                      key={key}
                      label={label}
                      value={item[key]}
                      onChange={(value) => updateComparable(item.order, { [key]: value })}
                    />
                  ))}
                  <button type="button" disabled={busy || !activeCase} onClick={() => saveComparable(item)}>
                    Lưu TSSS{String(item.order).padStart(2, '0')}
                  </button>
                </article>
              ))}
            </div>
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-adjustments">
            <h2 id="stage-adjustments">4. P0 + C1–C11 human decisions</h2>
            <Field label="Người chọn adjustment" value={decisionActor} onChange={setDecisionActor} />
            <div className="cenvalue-re-columns">
              {adjustments.map((item, index) => (
                <article className="cenvalue-re-card" key={item.order}>
                  <h3>TSSS{String(item.order).padStart(2, '0')} · {completedRates[index]}/11 decisions</h3>
                  <Field
                    label="Normalized base P0"
                    value={item.normalizedBase}
                    onChange={(value) => updateAdjustment(item.order, { normalizedBase: value })}
                  />
                  <Field
                    label="Evidence ref"
                    value={item.evidenceRef}
                    onChange={(value) => updateAdjustment(item.order, { evidenceRef: value })}
                  />
                  <button type="button" disabled={busy || !activeCase} onClick={() => bindBase(item)}>Bind P0</button>
                  <div className="cenvalue-re-rate-grid">
                    {FACTORS.map((factorKey) => {
                      const value = item.rates[factorKey];
                      const enteredZero = value !== '' && displayPercentToFraction(value) === '0';
                      return (
                        <div className="cenvalue-re-rate" key={factorKey}>
                          <Field
                            label={`${factorKey} (%)${enteredZero ? ' · đã nhập 0%' : ''}`}
                            value={value}
                            onChange={(next) =>
                              updateAdjustment(item.order, {
                                rates: { ...item.rates, [factorKey]: next },
                              })
                            }
                          />
                          <button
                            type="button"
                            disabled={busy || !activeCase || !decisionActor || value === ''}
                            onClick={() => saveRate(item, factorKey)}
                          >
                            Lưu {factorKey}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                  <button
                    type="button"
                    disabled={busy || !activeCase || completedRates[index] !== 11}
                    onClick={() => runAdjustment(item)}
                  >
                    Chạy adjustment
                  </button>
                  <ResultBox value={item.currentRun} empty="Chưa có current adjustment snapshot." />
                </article>
              ))}
            </div>
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-quality">
            <h2 id="stage-quality">5. Quality / 15% readiness</h2>
            <button type="button" disabled={busy || !activeCase} onClick={previewQuality}>Đọc quality/readiness</button>
            <ResultBox value={quality} />
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-indication">
            <h2 id="stage-indication">6. Human indication</h2>
            <div className="cenvalue-re-grid">
              <label className="cenvalue-re-field">
                <span>Kiểu lựa chọn</span>
                <select
                  value={indicationForm.selectionKind}
                  onChange={(event) =>
                    setIndicationForm((current) => ({ ...current, selectionKind: event.target.value }))
                  }
                >
                  <option value="COMPARABLE">Comparable</option>
                  <option value="ZERO_GROSS_AVERAGE">Zero-gross average</option>
                </select>
              </label>
              <Field
                label="TSSS được chọn (1–3)"
                value={indicationForm.selectedComparableOrder}
                disabled={indicationForm.selectionKind !== 'COMPARABLE'}
                onChange={(value) =>
                  setIndicationForm((current) => ({ ...current, selectedComparableOrder: value }))
                }
              />
              <Field
                label="Người xác nhận"
                value={indicationForm.confirmedBy}
                onChange={(value) => setIndicationForm((current) => ({ ...current, confirmedBy: value }))}
              />
              <Field
                label="Lý do"
                value={indicationForm.reason}
                onChange={(value) => setIndicationForm((current) => ({ ...current, reason: value }))}
              />
            </div>
            <button
              type="button"
              disabled={busy || !activeCase || !indicationForm.confirmedBy || !indicationForm.reason}
              onClick={confirmIndication}
            >
              Xác nhận human indication
            </button>
            <ResultBox value={indication} />
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-final">
            <h2 id="stage-final">7. Supplied construction + final valuation</h2>
            <div className="cenvalue-re-grid">
              <Field
                label="Construction aggregate (VND)"
                value={construction.amount}
                onChange={(value) => setConstruction((current) => ({ ...current, amount: value }))}
              />
              <Field
                label="Evidence ref"
                value={construction.evidenceRef}
                onChange={(value) => setConstruction((current) => ({ ...current, evidenceRef: value }))}
              />
              <Field
                label="Người cung cấp"
                value={construction.suppliedBy}
                onChange={(value) => setConstruction((current) => ({ ...current, suppliedBy: value }))}
              />
            </div>
            <div className="cenvalue-re-actions">
              <button type="button" disabled={busy || !activeCase} onClick={bindConstruction}>Bind construction aggregate</button>
              <button type="button" disabled={busy || !activeCase} onClick={composeFinal}>Compose final valuation</button>
            </div>
            <ResultBox value={finalValuation} />
          </section>

          <section className="cenvalue-re-panel" aria-labelledby="stage-export">
            <h2 id="stage-export">8. Workbook export</h2>
            <p className="cenvalue-re-muted">Generation success chỉ tạo workbook artifact; Microsoft Excel qualification vẫn NOT_RUN.</p>
            <div className="cenvalue-re-grid">
              <Field
                label="Supported source template path"
                value={exportForm.templatePath}
                onChange={(value) => setExportForm((current) => ({ ...current, templatePath: value }))}
              />
              <Field
                label="New output path"
                value={exportForm.outputPath}
                onChange={(value) => setExportForm((current) => ({ ...current, outputPath: value }))}
              />
            </div>
            <button type="button" disabled={busy || !activeCase} onClick={generateWorkbook}>Tạo workbook</button>
            <ResultBox value={exportArtifact} />
          </section>
        </main>
      </AppShell>
    </div>
  );
}

export default ReShell;
