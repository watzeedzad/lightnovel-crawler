import { UserAvatar } from '@/components/Tags/gravatar';
import {
  UserRoleTag,
  UserStatusTag,
  UserTierTag,
} from '@/components/Tags/users';
import type { User } from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatDate, formatFromNow } from '@/utils/time';
import {
  CalendarOutlined,
  CrownOutlined,
  MailOutlined,
  SafetyCertificateOutlined,
  UserOutlined,
} from '@ant-design/icons';
import {
  Button,
  Descriptions,
  Divider,
  Flex,
  Grid,
  Result,
  Space,
  Spin,
  Typography,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { UserActionButtons } from '../UserList/UserActionButtons';
import { UserEditButton } from './UserEditButton';

export const UserDetailsPage: React.FC<any> = () => {
  const { xs } = Grid.useBreakpoint();
  const { id } = useParams<{ id: string }>();

  const [user, setUser] = useState<User>();
  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    const fetchUser = async (id: string) => {
      setError(undefined);
      try {
        const { data } = await axios.get<User>(`/api/user/${id}`);
        setUser(data);
      } catch (err: any) {
        setError(stringifyError(err));
      } finally {
        setLoading(false);
      }
    };
    if (id) {
      fetchUser(id);
    }
  }, [id, refreshId]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !user) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load user details"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Typography.Title level={2}>
        <UserOutlined /> Profile
      </Typography.Title>

      <Descriptions
        bordered
        column={1}
        size="middle"
        layout={xs ? 'vertical' : 'horizontal'}
        styles={{ label: { width: 150, fontWeight: 500 } }}
      >
        <Descriptions.Item
          label={
            <Space>
              <UserOutlined /> Name
            </Space>
          }
        >
          <Space>
            <UserAvatar user={user} size={32} />
            <Typography.Text>{user.name}</Typography.Text>
            <Divider type="vertical" />
            <UserEditButton
              user={user}
              onChange={() => setRefreshId((v) => v + 1)}
            />
          </Space>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <MailOutlined /> Email
            </Space>
          }
        >
          <Typography.Text copyable>{user.email}</Typography.Text>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <SafetyCertificateOutlined /> Role
            </Space>
          }
        >
          <UserRoleTag value={user.role} />
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <CrownOutlined /> Tier
            </Space>
          }
        >
          <UserTierTag value={user.tier} />
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <UserOutlined /> Status
            </Space>
          }
        >
          <Space>
            <UserStatusTag value={user.is_active} />
            <Divider type="vertical" />
            <UserActionButtons
              user={user}
              onChange={() => setRefreshId((v) => v + 1)}
            />
          </Space>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <CalendarOutlined /> Joined
            </Space>
          }
        >
          <Typography.Text>{formatDate(user.created_at)}</Typography.Text>
          <Divider type="vertical" />
          <Typography.Text type="secondary">
            {formatFromNow(user.created_at)}
          </Typography.Text>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <CalendarOutlined /> Last Update
            </Space>
          }
        >
          <Typography.Text>{formatDate(user.updated_at)}</Typography.Text>
          <Divider type="vertical" />
          <Typography.Text type="secondary">
            {formatFromNow(user.updated_at)}
          </Typography.Text>
        </Descriptions.Item>
      </Descriptions>

      <Divider size="small" />

      <Typography.Paragraph
        type="secondary"
        style={{ marginBottom: 0, fontSize: 12 }}
      >
        Manage your identity, credentials, and subscription tier. Use the
        actions above to update your name or change your password.
      </Typography.Paragraph>
    </div>
  );
};
