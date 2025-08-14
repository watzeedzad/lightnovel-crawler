import { Flex, Select, Typography } from 'antd';
import { JobStatusFilterParams } from './constants';
import type { JobListHook } from './hooks';

export const JobFilterBox: React.FC<
  Pick<JobListHook, 'status' | 'updateParams'>
> = ({ status, updateParams }) => {
  return (
    <Flex align="center" gap={5}>
      <Typography.Text>Status:</Typography.Text>
      <Select
        allowClear
        defaultValue={status || JobStatusFilterParams[0].value}
        onChange={(status) => updateParams({ status })}
        placeholder="Filter by Status"
        style={{ minWidth: 150 }}
        options={JobStatusFilterParams}
      />
    </Flex>
  );
};
