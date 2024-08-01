import React from "react";
import { DarkThemeToggle, Navbar } from "flowbite-react";
import NavbarSignIn from "./NavbarSignIn";
import NavbarAvatar from "./NavbarAvatar";

export interface NavbarContainerProps {
  pathname?: string;
  children?: React.ReactNode;
}

export const NavbarDynamicContent = () => (
  <>
    <NavbarSignIn />
    <NavbarAvatar />
  </>
);

export const NavbarContainer: React.FC<NavbarContainerProps> = ({ pathname = "", children }) => {
  // Trim a triling '/' from the pathname unless it is also the leading '/'. We need to do this
  // because when rendering for static generation, pathnames have trailing '/'s but when generating
  // in local dev they do not.
  const trimmedPathname = pathname.replace(/^(.+)\/$/, (_, p1) => p1);

  const NavbarLink: React.FC<Omit<React.ComponentProps<typeof Navbar.Link>, "active">> = (
    props,
  ) => <Navbar.Link {...props} active={trimmedPathname === props.href} />;

  return (
    <Navbar fluid rounded>
      <Navbar.Brand className="pr-8">
        <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
          Components DB
        </span>
      </Navbar.Brand>
      <Navbar.Collapse>
        <NavbarLink href="/">Home</NavbarLink>
        <NavbarLink href="/api">GraphQL</NavbarLink>
      </Navbar.Collapse>
      <div className="flex-grow" />
      <div className="flex gap-2 items-center">
        <DarkThemeToggle />
        {children}
        <Navbar.Toggle />
      </div>
    </Navbar>
  );
};

export default NavbarContainer;
