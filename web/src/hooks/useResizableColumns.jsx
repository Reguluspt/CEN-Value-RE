import React, { useState } from 'react';

// Custom header cell component
const ResizableHeaderCell = (props) => {
  const { onResize, width, ...restProps } = props;

  if (!width) {
    return <th {...restProps} />;
  }

  return (
    <th {...restProps}>
      {props.children}
      <div
        className="resizable-handle"
        style={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: 8,
          cursor: 'col-resize',
          zIndex: 10,
        }}
        onMouseDown={(e) => {
          e.preventDefault();
          e.stopPropagation();
          const startX = e.pageX;
          const startWidth = width;

          const onMouseMove = (moveEvent) => {
            const newWidth = Math.max(50, startWidth + (moveEvent.pageX - startX));
            onResize(newWidth);
          };

          const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
          };

          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp);
        }}
      />
    </th>
  );
};

export function useResizableColumns(tableKey, initialWidths = {}, widthConstraints = {}) {
  const constrainWidth = (key, width) => {
    const numericWidth = parseFloat(width) || 120;
    const limits = widthConstraints[key] || {};
    const minWidth = Number.isFinite(limits.min) ? limits.min : 50;
    const maxWidth = Number.isFinite(limits.max) ? limits.max : Number.POSITIVE_INFINITY;
    return Math.min(maxWidth, Math.max(minWidth, numericWidth));
  };

  const [widths, setWidths] = useState(() => {
    let storedWidths = initialWidths;
    if (tableKey) {
      const saved = localStorage.getItem(`table_widths_${tableKey}`);
      if (saved) {
        try {
          storedWidths = JSON.parse(saved);
        } catch (e) {
          // ignore parsing error and fallback
        }
      }
    }
    return Object.fromEntries(
      Object.entries(storedWidths).map(([key, width]) => [key, constrainWidth(key, width)])
    );
  });

  const handleResize = (key) => (newWidth) => {
    setWidths((prev) => {
      const updated = {
        ...prev,
        [key]: constrainWidth(key, newWidth),
      };
      if (tableKey) {
        localStorage.setItem(`table_widths_${tableKey}`, JSON.stringify(updated));
      }
      return updated;
    });
  };

  const getResizableProps = (columns) => {
    const resizableColumns = columns.map((col) => {
      // Don't make action columns or special columns without key/dataIndex resizable
      if (!col.key && !col.dataIndex) return col;
      const key = col.key || col.dataIndex;
      const currentWidth = widths[key] || col.width || 120;
      
      // If width is represented as a percentage string (e.g. '16%'),
      // convert it to a default numeric width
      const numericWidth = typeof currentWidth === 'string' && currentWidth.endsWith('%')
        ? (parseFloat(currentWidth) / 100) * 1000 
        : parseFloat(currentWidth) || 120;

      return {
        ...col,
        width: constrainWidth(key, numericWidth),
        onHeaderCell: (column) => ({
          width: column.width,
          onResize: handleResize(key),
        }),
      };
    });

    return {
      columns: resizableColumns,
      components: {
        header: {
          cell: ResizableHeaderCell,
        },
      },
    };
  };

  return { getResizableProps, widths };
}
