import React from "react";
import { Avatar, Menu, Space } from "antd";
import type { MenuProps } from "antd";
import { DownOutlined } from "@ant-design/icons";

import { useAuth } from "../hooks";

export interface UserDropdownProps extends Omit<MenuProps, "items"> {
  displayName?: React.ReactNode;
  avatarUrl?: string;
  avatarLabel?: string;
}

export const UserDropdown: React.FC<UserDropdownProps> = ({
  displayName = "",
  avatarUrl,
  avatarLabel,
  ...props
}) => {
  const auth = useAuth();

  const items: MenuProps["items"] = [
    {
      key: "user",
      label: (
        <Space>
          {(avatarLabel || avatarUrl) && <Avatar src={avatarUrl}>{avatarLabel}</Avatar>}
          {displayName}
          <DownOutlined />
        </Space>
      ),
      children: [
        {
          key: "signout",
          label: "Sign out",
        },
      ],
    },
  ];

  return (
    <Menu
      mode="horizontal"
      theme="dark"
      selectable={false}
      items={items}
      onClick={({ key }) => {
        if (key === "signout") {
          auth && auth.signOut();
        }
      }}
      {...props}
    />
  );
};

export default UserDropdown;
