import React from "react";
import { theme, Flex } from "antd";
import { useNavigate } from "react-router-dom";

import { SignInOrUpForm } from ".";
import { DefaultPage } from ".";

export const SignInOrUpPage: React.FC<
  Omit<React.ComponentProps<typeof SignInOrUpForm>, "onSuccess">
> = (props) => {
  const { token } = theme.useToken();
  const navigate = useNavigate();

  return (
    <DefaultPage>
      <Flex vertical style={{ position: "absolute", left: 0, right: 0, top: 0, bottom: 0 }}>
        <div style={{ flexGrow: 1 }} />
        <div
          style={{
            maxWidth: 0.8 * token.screenSM,
            marginLeft: "auto",
            marginRight: "auto",
            border: `1px solid ${token.colorBorder}`,
            borderRadius: token.borderRadiusLG,
            backgroundColor: token.colorBgElevated,
            padding: token.paddingLG,
          }}
        >
          <SignInOrUpForm
            onSuccess={() => {
              navigate("/");
            }}
            {...props}
          />
        </div>
        <div style={{ flexGrow: 3 }} />
      </Flex>
    </DefaultPage>
  );
};

export default SignInOrUpPage;
