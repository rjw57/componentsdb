import React from "react";
import { Modal } from "flowbite-react";

import SignInOrUpForm from "../components/SignInOrUpForm";

type UseSignInOrSignUpModalReturnValue = [(type: "sign_in" | "sign_up") => void, React.ReactNode];

export const useSignInOrSignUpModal = (): UseSignInOrSignUpModalReturnValue => {
  const [isModalOpen, setIsModalOpen] = React.useState<boolean>(false);
  const [type, setType] = React.useState<"sign_in" | "sign_up">("sign_in");

  const showModal = (type: "sign_in" | "sign_up") => {
    setType(type);
    setIsModalOpen(true);
  };

  const contextHolder = (
    <Modal size="sm" show={isModalOpen} onClose={() => setIsModalOpen(false)} popup>
      <Modal.Header />
      <Modal.Body>
        <SignInOrUpForm
          initialType={type}
          onSuccess={() => {
            setIsModalOpen(false);
          }}
        />
      </Modal.Body>
    </Modal>
  );

  return [showModal, contextHolder];
};

export default useSignInOrSignUpModal;
