import React from "react";
import { DarkThemeToggle, Navbar } from "flowbite-react";
import Link from "next/link";

export interface NavbarContainerProps {
  pathname?: string;
  signInContent?: React.ReactNode;
  avatarContent?: React.ReactNode;
}

export const NavbarContainer: React.FC<NavbarContainerProps> = ({
  pathname = "",
  signInContent,
  avatarContent,
}) => (
  <Navbar fluid rounded>
    <Navbar.Brand className="pr-8">
      <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
        Components DB
      </span>
    </Navbar.Brand>
    <Navbar.Collapse>
      <Navbar.Link as={Link} href="/" active={pathname === "/"}>
        Home
      </Navbar.Link>
      <Navbar.Link as={Link} href="/api" active={pathname == "/api"}>
        GraphQL
      </Navbar.Link>
    </Navbar.Collapse>
    <div className="flex-grow" />
    <div className="flex gap-4 items-center">
      <DarkThemeToggle />
      {signInContent}
      {avatarContent}
      <Navbar.Toggle />
    </div>
  </Navbar>
);

export default NavbarContainer;
