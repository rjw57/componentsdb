import { Button } from "flowbite-react";

import useSignInOrSignUpModal from "../hooks/useSignInOrSignUpModal";
import useSignIn from "../hooks/useSignIn";

export const NavBarSignIn = () => {
  const [showSignIn, signInContextHolder] = useSignInOrSignUpModal();
  const { isSignedIn } = useSignIn();

  return (
    <>
      {!isSignedIn && (
        <>
          <Button color="gray" size="xs" onClick={() => showSignIn("sign_in")}>
            Sign in
          </Button>
          <Button size="xs" onClick={() => showSignIn("sign_up")}>
            Sign up
          </Button>
        </>
      )}
      {signInContextHolder}
    </>
  );
};

export default NavBarSignIn;
