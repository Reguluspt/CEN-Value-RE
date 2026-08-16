# Application Source Baseline Validation

**Date:** 2026-08-16
**Reference:** `Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff:web/`

## Results
- E0-PR-001 architecture suite: PASS (workflow step completed)
- npm ci exit: `0`
- npm lint exit: `1`
- npm build exit: `0`

Exit 0 means PASS. Exit 125 means NOT RUN because npm ci failed.

## npm ci log
```text
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/config-array@0.23.5',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/config-helpers@0.6.0',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/core@1.2.1',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/js@10.0.1',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/object-schema@3.0.5',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: '@eslint/plugin-kit@0.7.2',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'eslint@10.5.0',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'eslint-scope@9.1.2',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'eslint-visitor-keys@5.0.1',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'espree@11.2.0',
npm warn EBADENGINE   required: { node: '^20.19.0 || ^22.13.0 || >=24' },
npm warn EBADENGINE   current: { node: 'v22.12.0', npm: '10.9.0' }
npm warn EBADENGINE }

added 276 packages, and audited 277 packages in 8s

44 packages are looking for funding
  run `npm fund` for details

5 high severity vulnerabilities

To address all issues, run:
  npm audit fix

Run `npm audit` for details.
```

## lint log
```text

> web@0.0.0 lint
> eslint .


/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/ErrorBoundary.jsx
  60:14  error  'process' is not defined  no-undef

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/ProtectedRoute.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/cases/CaseFilterBar.jsx
   1:8   error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           no-unused-vars
   2:56  error    'Badge' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           no-unused-vars
  20:5   error    'statuses' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               no-unused-vars
  39:6   warning  React Hook useEffect has missing dependencies: 'filters' and 'onFilterChange'. Either include them or remove the dependency array. If 'onFilterChange' changes too often, find the parent component that defines it and wrap that definition in useCallback                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 react-hooks/exhaustive-deps
  43:5   error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  41 |   // Sync internal search state when filters are cleared externally
  42 |   useEffect(() => {
> 43 |     setSearchText(filters.search || '');
     |     ^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  44 |   }, [filters.search]);
  45 |
  46 |   const handleChange = (key, value) => {  react-hooks/set-state-in-effect

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/cases/CaseImportModal.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/cases/CaseTable.jsx
     1:8   error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        no-unused-vars
     4:3   error    'EditOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 no-unused-vars
    10:3   error    'FolderOpenOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           no-unused-vars
    12:3   error    'InteractionOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
    13:3   error    'EyeOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  no-unused-vars
   168:14  error    'e' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            no-unused-vars
   200:16  error    'fallbackErr' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  no-unused-vars
   516:9   error    'handleDownloadPhathanhDocx' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   552:5   error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  550 |
  551 |   useEffect(() => {
> 552 |     fetchCases();
      |     ^^^^^^^^^^ Avoid calling setState() directly within an effect
  553 |   }, [filters]);
  554 |
  555 |   const handleTableChange = (pagination, tableFilters, sorter) => {  react-hooks/set-state-in-effect
   553:6   warning  React Hook useEffect has a missing dependency: 'fetchCases'. Either include it or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            react-hooks/exhaustive-deps
   572:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   590:18  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   606:52  error    'moment' is not defined                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  no-undef
   612:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   618:9   error    'handleOpenNotes' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     no-unused-vars
   625:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   643:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   673:9   error    'getStatusTag' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        no-unused-vars
   689:9   error    'formatDateOnly' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      no-unused-vars
   707:14  error    'e' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            no-unused-vars
   707:17  error    Empty block statement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    no-empty
   716:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   741:14  error    'e' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            no-unused-vars
   741:17  error    Empty block statement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    no-empty
  1081:9   error    'rowSelection' is assigned a value but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/cases/DocumentPreview.jsx
  1:8   error  'React' is defined but never used  no-unused-vars
  2:42  error  'Spin' is defined but never used   no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/cases/SendEmailModal.jsx
  1:8   error  'React' is defined but never used   no-unused-vars
  2:55  error  'Button' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/dashboard/RecentCases.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/dashboard/StatusDonut.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/EntryForm.jsx
    1:8   error  'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         no-unused-vars
    3:42  error  'UserOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  no-unused-vars
    3:56  error  'HomeOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  no-unused-vars
  225:5   error  Error: Cannot access variable before it is declared

`fetchFormOptions` is accessed before it is declared, which prevents the earlier access from updating when this value changes over time.

  223 |
  224 |   useEffect(() => {
> 225 |     fetchFormOptions();
      |     ^^^^^^^^^^^^^^^^ `fetchFormOptions` accessed before it is declared
  226 |     fetchOrganizations();
  227 |   }, []);
  228 |

  249 |   }, [formValues, form]);
  250 |
> 251 |   const fetchFormOptions = async () => {
      |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 252 |     setLoadingOptions(true);
      | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 253 |     try {
      …
      | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 261 |     }
      | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 262 |   };
      | ^^^^^ `fetchFormOptions` is declared here
  263 |
  264 |   const handleBranchChange = (value) => {
  265 |     setSelectedBranch(value);                                     react-hooks/immutability
  226:5   error  Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  224 |   useEffect(() => {
  225 |     fetchFormOptions();
> 226 |     fetchOrganizations();
      |     ^^^^^^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  227 |   }, []);
  228 |
  229 |   useEffect(() => {  react-hooks/set-state-in-effect

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/FileUploader.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/PageViewer.jsx
   1:8  error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                no-unused-vars
  40:5  error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  38 |   useEffect(() => {
  39 |     // Reset zoom and rotation when file changes
> 40 |     setZoom(1);
     |     ^^^^^^^ Avoid calling setState() directly within an effect
  41 |   }, [activeFile]);
  42 |
  43 |   useEffect(() => {  react-hooks/set-state-in-effect
  45:6  warning  React Hook useEffect has a missing dependency: 'fitToContainer'. Either include it or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                react-hooks/exhaustive-deps
  52:6  warning  React Hook useEffect has a missing dependency: 'fitToContainer'. Either include it or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                react-hooks/exhaustive-deps

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/SoboEntry.jsx
    1:8   error  'React' is defined but never used                       no-unused-vars
   61:10  error  'assetSubType' is assigned a value but never used       no-unused-vars
   61:24  error  'setAssetSubType' is assigned a value but never used    no-unused-vars
  254:13  error  'thua' is assigned a value but never used               no-unused-vars
  255:13  error  'to' is assigned a value but never used                 no-unused-vars
  297:9   error  'handleAddressBlur' is assigned a value but never used  no-unused-vars
  388:14  error  'err' is defined but never used                         no-unused-vars
  411:14  error  'err' is defined but never used                         no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/SwapAddressButton.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/entry/assetDescription.js
  9:31  error  Unnecessary escape character: \*  no-useless-escape

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/sobo/SoboDetailDrawer.jsx
   1:8  error  'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             no-unused-vars
  13:7  error  Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  11 |   useEffect(() => {
  12 |     if (open && record) {
> 13 |       setLoadingFiles(true);
     |       ^^^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  14 |       getSoboFiles(record.id)
  15 |         .then((res) => {
  16 |           setFiles(res.data);  react-hooks/set-state-in-effect

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/sobo/SoboEditModal.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/sobo/SoboTable.jsx
   1:8  error  'React' is defined but never used   no-unused-vars
  37:3  error  'onEdit' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/components/tasks/TaskModal.jsx
   1:8  error  'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        no-unused-vars
  90:5  error  Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  88 |     if (!open) return;
  89 |
> 90 |     setLoadingCases(true);
     |     ^^^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  91 |     client.get('/cases', { params: { page: 1, size: 500 } })
  92 |       .then((response) => {
  93 |         const cases = response.data?.items || [];  react-hooks/set-state-in-effect

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/hooks/useAuth.jsx
   1:8   error  'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
  19:14  error  'error' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
  27:5   error  Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  25 |
  26 |   useEffect(() => {
> 27 |     checkSession();
     |     ^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  28 |   }, []);
  29 |
  30 |   const login = async (username, password) => {  react-hooks/set-state-in-effect
  69:17  error  Fast refresh only works when a file only exports components. Use a new file to share constants or functions between components                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             react-refresh/only-export-components

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/hooks/useResizableColumns.jsx
   1:8   error  'React' is defined but never used                                                                                                                                    no-unused-vars
   4:7   error  Fast refresh only works when a file only exports components. Move your component(s) to a separate file. If all exports are HOCs, add them to the `extraHOCs` option  react-refresh/only-export-components
  65:18  error  'e' is defined but never used                                                                                                                                        no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/CaseDetail.jsx
   1:8  error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   no-unused-vars
   5:3  error    'Form' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    no-unused-vars
  42:7  error    Error: Cannot access variable before it is declared

`fetchCaseData` is accessed before it is declared, which prevents the earlier access from updating when this value changes over time.

  40 |   useEffect(() => {
  41 |     if (id) {
> 42 |       fetchCaseData();
     |       ^^^^^^^^^^^^^ `fetchCaseData` accessed before it is declared
  43 |       fetchNotes();
  44 |       fetchRelatedTasks();
  45 |     }

  46 |   }, [id]);
  47 |
> 48 |   const fetchCaseData = async () => {
     |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 49 |     setLoading(true);
     | ^^^^^^^^^^^^^^^^^^^^^
> 50 |     try {
     …
     | ^^^^^^^^^^^^^^^^^^^^^
> 58 |     }
     | ^^^^^^^^^^^^^^^^^^^^^
> 59 |   };
     | ^^^^^ `fetchCaseData` is declared here
  60 |
  61 |   const fetchNotes = async () => {
  62 |     setLoadingNotes(true);                                            react-hooks/immutability
  43:7  error    Error: Cannot access variable before it is declared

`fetchNotes` is accessed before it is declared, which prevents the earlier access from updating when this value changes over time.

  41 |     if (id) {
  42 |       fetchCaseData();
> 43 |       fetchNotes();
     |       ^^^^^^^^^^ `fetchNotes` accessed before it is declared
  44 |       fetchRelatedTasks();
  45 |     }
  46 |   }, [id]);

  59 |   };
  60 |
> 61 |   const fetchNotes = async () => {
     |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 62 |     setLoadingNotes(true);
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 63 |     try {
     …
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 70 |     }
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 71 |   };
     | ^^^^^ `fetchNotes` is declared here
  72 |
  73 |   const fetchRelatedTasks = async () => {
  74 |     setLoadingTasks(true);                                                  react-hooks/immutability
  44:7  error    Error: Cannot access variable before it is declared

`fetchRelatedTasks` is accessed before it is declared, which prevents the earlier access from updating when this value changes over time.

  42 |       fetchCaseData();
  43 |       fetchNotes();
> 44 |       fetchRelatedTasks();
     |       ^^^^^^^^^^^^^^^^^ `fetchRelatedTasks` accessed before it is declared
  45 |     }
  46 |   }, [id]);
  47 |

  71 |   };
  72 |
> 73 |   const fetchRelatedTasks = async () => {
     |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> 74 |     setLoadingTasks(true);
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 75 |     try {
     …
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 83 |     }
     | ^^^^^^^^^^^^^^^^^^^^^^^^^^
> 84 |   };
     | ^^^^^ `fetchRelatedTasks` is declared here
  85 |
  86 |   const handleCreateRelatedTask = async (payload) => {
  87 |     await client.post('/tasks', {  react-hooks/immutability
  46:6  warning  React Hook useEffect has missing dependencies: 'fetchCaseData', 'fetchNotes', and 'fetchRelatedTasks'. Either include them or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           react-hooks/exhaustive-deps

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/Cases.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/Entry.jsx
   48:7    error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  46 |     const tabFromUrl = searchParams.get('tab') === 'sobo' ? 'sobo' : 'appraisal';
  47 |     if (tabFromUrl !== activeTab) {
> 48 |       setActiveTab(tabFromUrl);
     |       ^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  49 |     }
  50 |   }, [searchParams]);
  51 |  react-hooks/set-state-in-effect
   50:6    warning  React Hook useEffect has a missing dependency: 'activeTab'. Either include it or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 react-hooks/exhaustive-deps
  203:127  error    'fileIdx' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/HealthCheck.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/Login.jsx
  1:8  error  'React' is defined but never used  no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/Settings.jsx
    1:8   error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        no-unused-vars
   32:3   error    'CheckCircleOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
   33:3   error    'CloseCircleOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars
  215:7   error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  213 |       exchangeCode();
  214 |     } else {
> 215 |       fetchSettings();
      |       ^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  216 |     }
  217 |   }, [searchParams]);
  218 |  react-hooks/set-state-in-effect
  217:6   warning  React Hook useEffect has missing dependencies: 'fetchSettings' and 'setSearchParams'. Either include them or remove the dependency array                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 react-hooks/exhaustive-deps
  343:14  error    'err' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          no-unused-vars

/home/runner/work/CEN-Value-RE/CEN-Value-RE/web/src/pages/Sobo.jsx
    1:8  error    'React' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               no-unused-vars
    9:3  error    'ExclamationCircleOutlined' is defined but never used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           no-unused-vars
  107:6  warning  React Hook useCallback has a missing dependency: 'pagination'. Either include it or remove the dependency array. Mutable values like 'pagination.current' aren't valid dependencies because mutating them doesn't re-render the component                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       react-hooks/exhaustive-deps
  111:5  error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  109 |   // Load initial data
  110 |   useEffect(() => {
> 111 |     fetchStats();
      |     ^^^^^^^^^^ Avoid calling setState() directly within an effect
  112 |   }, [fetchStats]);
  113 |
  114 |   useEffect(() => {               react-hooks/set-state-in-effect
  115:5  error    Error: Calling setState synchronously within an effect can trigger cascading renders

Effects are intended to synchronize state between React and external systems such as manually updating the DOM, state management libraries, or other platform APIs. In general, the body of an effect should do one or both of the following:
* Update external systems with the latest state from React.
* Subscribe for updates from some external system, calling setState in a callback function when external state changes.

Calling setState synchronously within an effect body causes cascading renders that can hurt performance, and is not recommended. (https://react.dev/learn/you-might-not-need-an-effect).

  113 |
  114 |   useEffect(() => {
> 115 |     fetchRecords();
      |     ^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  116 |   }, [fetchRecords]);
  117 |
  118 |   // Handle table pagination, sorting & filtering  react-hooks/set-state-in-effect

✖ 96 problems (88 errors, 8 warnings)

```

## build log
```text

> web@0.0.0 build
> vite build

[36mvite v8.1.0 [32mbuilding client environment for production...[36m[39m
[2Ktransforming...✓ 1895 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                             0.45 kB │ gzip:   0.29 kB
dist/assets/cenvalue-logo-DAXmZm-0.png     30.57 kB
dist/assets/index-D80jgUSH.css              2.56 kB │ gzip:   0.99 kB
dist/assets/index-Cu7t_Y-0.js           2,394.55 kB │ gzip: 704.30 kB

[33m[33m[INEFFECTIVE_DYNAMIC_IMPORT] [0msrc/api/cases.js is dynamically imported by src/components/cases/CaseTable.jsx but also statically imported by src/components/cases/CaseEditModal.jsx, src/components/cases/CaseFilterBar.jsx, src/components/cases/CaseImportModal.jsx, src/components/cases/CaseRevenue.jsx, src/components/cases/CaseTable.jsx, ..., dynamic import will not move module into another chunk.
[39m
[33m[plugin builtin:vite-reporter] 
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rolldownOptions.output.codeSplitting to improve chunking: https://rolldown.rs/reference/OutputOptions.codeSplitting
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.[39m
[32m✓ built in 1.05s[39m
```
