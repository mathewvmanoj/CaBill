import React from "react";
import { Box, VStack, IconButton, Image } from "@chakra-ui/react";
import {
  BsCalendar3,
  BsFileEarmarkText,
  BsPeople,
  BsPerson,
} from "react-icons/bs";
import logo from "../../assets/logo.png";

const Sidebar = () => {
  const ICON_SIZE = 28;
  return (
    <Box
      w="100px"
      h="100vh"
      bg="brand.800"
      position="fixed"
      left={0}
      top={0}
      py={8}
    >
      <VStack spacing={8}>
        <Image src={logo} alt="Fintrack Logo" w="110px" h="110px" />
        <VStack spacing={6}>
          <IconButton
            aria-label="Schedule"
            icon={<BsCalendar3 size={ICON_SIZE} />}
            variant="ghost"
            color="white"
            size="lg"
          />
          <IconButton
            aria-label="Reports"
            icon={<BsFileEarmarkText size={ICON_SIZE} />}
            variant="ghost"
            color="white"
            size="lg"
          />
          <IconButton
            aria-label="Groups"
            icon={<BsPeople size={ICON_SIZE} />}
            variant="ghost"
            color="white"
            size="lg"
          />
          <IconButton
            aria-label="Profile"
            icon={<BsPerson size={ICON_SIZE} />}
            variant="ghost"
            color="white"
            size="lg"
          />
        </VStack>
      </VStack>
    </Box>
  );
};

export default Sidebar;
