import { useState } from 'react';
import { AppShell } from '@astryxdesign/core/AppShell';
import { FormLayout } from '@astryxdesign/core/FormLayout';
import { SideNav, SideNavItem, SideNavSection } from '@astryxdesign/core/SideNav';
import { Text } from '@astryxdesign/core/Text';
import { TextInput } from '@astryxdesign/core/TextInput';
import { Theme } from '@astryxdesign/core/theme';
import { neutralTheme } from '@astryxdesign/theme-neutral/built';
import './astryx.css';

function ReShell() {
  const [caseCode, setCaseCode] = useState('');
  const [propertyAddress, setPropertyAddress] = useState('');

  const sideNav = (
    <SideNav>
      <SideNavSection title="CenValue RE">
        <SideNavItem label="Integration spike" href="/re" isSelected />
        <SideNavItem label="Legacy dashboard" href="/dashboard" />
      </SideNavSection>
    </SideNav>
  );

  return (
    <Theme theme={neutralTheme}>
      <div className="cenvalue-re-surface" data-re-astryx-spike="v1">
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
    </Theme>
  );
}

export default ReShell;
