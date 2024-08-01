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

export const NavbarContainer: React.FC<NavbarContainerProps> = ({ pathname = "", children }) => (
  <Navbar fluid rounded>
    <Navbar.Brand className="pr-8">
      <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
        Components DB
      </span>
    </Navbar.Brand>
    <Navbar.Collapse>
      <Navbar.Link href="/" active={pathname === "/"}>
        Home
      </Navbar.Link>
      <Navbar.Link href="/api" active={pathname === "/api"}>
        GraphQL
      </Navbar.Link>
    </Navbar.Collapse>
    <div className="flex-grow" />
    <div className="flex gap-2 items-center">
      <DarkThemeToggle />
      {children}
      <Navbar.Toggle />
    </div>
  </Navbar>
);

export default NavbarContainer;
