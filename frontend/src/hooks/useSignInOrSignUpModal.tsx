import { theme, Modal } from "antd";

import { SignInOrUpForm } from "../components";

type UseSignInOrSignUpModalReturnValue = [
  (type: "sign_in" | "sign_up") => void,
  ReturnType<typeof Modal.useModal>[1],
];

export const useSignInOrSignUpModal = (): UseSignInOrSignUpModalReturnValue => {
  const [modal, contextHolder] = Modal.useModal();
  const { token } = theme.useToken();

  const showModal = (type: "sign_in" | "sign_up") => {
    const newModal = modal.info({
      icon: <></>,
      closable: true,
      footer: null,
      width: Math.floor(0.8 * token.screenXS),
      content: (
        <SignInOrUpForm
          type={type}
          onSuccess={() => {
            newModal.destroy();
          }}
        />
      ),
    });
  };

  return [showModal, contextHolder];
};

export default useSignInOrSignUpModal;
