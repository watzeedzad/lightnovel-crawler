import type { User } from '@/types';
import { stringifyError } from '@/utils/errors';
import { EditOutlined, SaveOutlined } from '@ant-design/icons';
import {
  Button,
  Divider,
  Flex,
  Form,
  Input,
  Modal,
  Space,
  message,
} from 'antd';
import axios from 'axios';
import { useState } from 'react';

export const ProfileNameChangeButton: React.FC<{
  user: User;
  onDone: () => Promise<any>;
}> = ({ user, onDone }) => {
  const [messageApi, contextHolder] = message.useMessage();

  const [editOpen, setEditOpen] = useState(false);
  const [updating, setUpdating] = useState(false);

  const handleUpdateName = async (values: { name: string }) => {
    try {
      setUpdating(true);
      await axios.put('/api/auth/me/name', {
        name: values.name.trim(),
      });
      await onDone();
      messageApi.success('Name updated successfully');
      setEditOpen(false);
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setUpdating(false);
    }
  };

  return (
    <>
      <Button
        size="small"
        shape="round"
        icon={<EditOutlined />}
        onClick={() => setEditOpen(true)}
      >
        Edit
      </Button>

      <Modal
        title={
          <Space>
            <EditOutlined /> Edit Name
          </Space>
        }
        open={editOpen}
        footer={null}
        onCancel={() => setEditOpen(false)}
        destroyOnHidden
      >
        {contextHolder}
        <Form
          size="large"
          layout="vertical"
          onFinish={handleUpdateName}
          initialValues={{ name: user.name }}
        >
          <Form.Item
            name="name"
            label="Full Name"
            rules={[
              { required: true, message: 'Please enter your name' },
              { min: 2, message: 'Name must be at least 2 characters' },
            ]}
          >
            <Input placeholder="Your display name" maxLength={100} allowClear />
          </Form.Item>

          <Divider size="small" />

          <Flex gap={10} justify="end">
            <Button onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button
              type="primary"
              htmlType="submit"
              loading={updating}
              icon={<SaveOutlined />}
            >
              Save
            </Button>
          </Flex>
        </Form>
      </Modal>
    </>
  );
};
