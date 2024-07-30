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
      <div
        style={{
          maxWidth: 0.8 * token.screenXS,
          marginLeft: "auto",
          marginRight: "auto",
          border: `1px solid ${token.colorBorder}`,
          borderRadius: token.borderRadiusLG,
          backgroundColor: token.colorBgElevated,
          paddingTop: token.paddingContentVerticalLG,
          paddingBottom: token.paddingContentVerticalLG,
          paddingRight: token.paddingContentHorizontalLG,
          paddingLeft: token.paddingContentHorizontalLG,
        }}
      >
        <SignInOrUpForm
          onSuccess={() => {
            navigate("/");
          }}
          {...props}
        />
      </div>
    </DefaultPage>
  );
};

export default SignInOrUpPage;
