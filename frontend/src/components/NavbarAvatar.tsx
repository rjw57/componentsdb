import { Avatar, Dropdown } from "flowbite-react";

import useSignIn from "../hooks/useSignIn";

export const NavbarAvatar = () => {
  const { isSignedIn, authenticatedUser, signOut } = useSignIn();

  if (!isSignedIn) {
    return null;
  }

  return (
    <Dropdown
      arrowIcon={false}
      inline
      label={
        <Avatar
          size="sm"
          alt={authenticatedUser?.displayName}
          img={authenticatedUser?.avatarUrl}
          placeholderInitials={`${authenticatedUser?.displayName}`.substring(0, 1)}
        />
      }
    >
      <Dropdown.Header>
        <span className="block text-sm">{authenticatedUser?.displayName}</span>
        <span className="block truncate text-sm font-medium">{authenticatedUser?.email}</span>
      </Dropdown.Header>
      <Dropdown.Item onClick={signOut}>Sign out</Dropdown.Item>
    </Dropdown>
  );
};

export default NavbarAvatar;
