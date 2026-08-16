import { useState } from 'react';
import { AppShell } from '@astryxdesign/core/AppShell';
import { FormLayout } from '@astryxdesign/core/FormLayout';
import { SideNav, SideNavItem, SideNavSection } from '@astryxdesign/core/SideNav';
import { Text } from '@astryxdesign/core/Text';
import { TextInput } from '@astryxdesign/core/TextInput';
import './astryx.css';

function ReShell() {
  const [caseCode, setCaseCode] = useState('');
  const [propertyAddress, setPropertyAddress] = useState('');
  const themeMode =
    typeof document !== 'undefined' && document.documentElement.dataset.theme === 'dark'
      ? 'dark'
      : 'light';

  const sideNav = (
    <SideNav>
      <SideNavSection title="CenValue RE">
        <SideNavItem label="Integration spike" href="/re" isSelected />
        <SideNavItem label="Legacy dashboard" href="/dashboard" />
      </SideNavSection>
    </SideNav>
  );

  return (
    <div
      className="cenvalue-re-surface"
      data-astryx-theme="neutral"
      data-theme={themeMode}
      data-re-astryx-spike="v1"
    >
      <AppShell contentPadding={0} sideNav={sideNav}>
        <main className="cenvalue-re-spike-content">
          <div className="cenvalue-re-spike-heading">
            <Text type="large">CenValue RE — Astryx integration spike</Text>
            <Text type="body">
              Surface thử nghiệm độc lập để kiểm tra AppShell, SideNav và FormLayout.
            </Text>
          </div>

          <section className="cenvalue-re-spike-form" aria-label="RE form spike">
            <FormLayout>
              <TextInput
                label="Mã hồ sơ"
                value={caseCode}
                onChange={setCaseCode}
              />
              <TextInput
                label="Địa chỉ tài sản"
                value={propertyAddress}
                onChange={setPropertyAddress}
              />
            </FormLayout>
          </section>
        </main>
      </AppShell>
    </div>
  );
}

export default ReShell;
