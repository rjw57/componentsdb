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
        <div className="hover:brightness-125">
          <Avatar
            size="sm"
            alt={authenticatedUser?.displayName}
            bordered
            rounded
            img={({ className }) => (
              <>
                {/*
                This is some HTML magic which provides a falback user icon if the avatar image
                fails to load.
              */}
                <div className={`relative overflow-clip ${className}`}>
                  <svg
                    className="absolute top-0 bottom-0 left-0 right-0 bg-gray-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                      clip-rule="evenodd"
                    ></path>
                  </svg>
                  <img
                    className="absolute top-0 bottom-0 left-0 right-0"
                    src={authenticatedUser?.avatarUrl}
                  />
                </div>
              </>
            )}
            placeholderInitials={`${authenticatedUser?.displayName}`.substring(0, 1)}
          />
        </div>
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
