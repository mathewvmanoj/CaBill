import React, { useState } from "react";
import {
  Box,
  Flex,
  Text,
  Heading,
  Input,
  Button,
  FormControl,
  FormLabel,
  Checkbox,
  Link,
  Container,
  VStack,
  useColorModeValue,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  useToast,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const navigate = useNavigate();
  const toast = useToast();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });

  // Content configurations for different user types
  const userTypes = {
    faculty: {
      title: "Faculty Portal",
      tagline: "Effortlessly create, manage, and optimize your class Timesheet",
      welcomeText:
        "Welcome back! Please log in to manage your class timesheet.",
      redirectPath: "/faculty/dashboard",
    },
    admin: {
      title: "Admin Portal",
      tagline:
        "Comprehensive control over institutional scheduling and management",
      welcomeText: "Welcome back! Access your administrative dashboard.",
      redirectPath: "/admin/dashboard",
    },
  };

  const [activeUserType, setActiveUserType] = useState("faculty");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Example API call - replace with your actual API endpoint
      const response = await loginUser(formData, activeUserType);

      //   if (response.success) {
      if (true) {
        toast({
          title: "Login Successful",
          description: `Welcome back to the ${activeUserType} portal!`,
          status: "success",
          duration: 3000,
        });

        // Store user data in localStorage or context
        // localStorage.setItem("userType", activeUserType);
        // localStorage.setItem("token", response.token);

        // Redirect to appropriate dashboard
        navigate(userTypes[activeUserType].redirectPath);
      }
    } catch (error) {
      toast({
        title: "Login Failed",
        description: error.message || "Please check your credentials",
        status: "error",
        duration: 3000,
      });
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  return (
    <Flex minH="100vh" direction={{ base: "column", md: "row" }}>
      {/* Left Panel */}
      <Box
        flex="1"
        bg="#0a0b2e"
        position="relative"
        p={8}
        display="flex"
        alignItems="center"
        justifyContent="center"
        overflow="hidden"
      >
        {/* Decorative Circles */}
        <Box
          position="absolute"
          top="-100px"
          left="-100px"
          w="380px"
          h="320px"
          borderRadius="full"
          bg="whiteAlpha.300"
        />
        <Box
          position="absolute"
          bottom="-100px"
          right="-100px"
          w="360px"
          h="340px"
          borderRadius="full"
          bg="whiteAlpha.400"
        />

        {/* Main Tagline */}
        <Heading
          color="white"
          fontSize={{ base: "3xl", lg: "6xl" }}
          lineHeight="1.2"
          zIndex={1}
          fontFamily="'Plus Jakarta Sans', sans-serif"
          fontWeight="300"
          maxWidth={{ base: "100%", lg: "80%" }}
          letterSpacing="-0.02em"
        >
          {userTypes[activeUserType].tagline}
        </Heading>
      </Box>

      {/* Right Panel */}
      <Flex flex="1" p={8} align="center">
        <Container p={0} maxW={{ base: "100%", md: "400px", lg: "85%" }}>
          <VStack spacing={8} align="stretch">
            <Tabs
              isFitted
              variant="soft-rounded"
              colorScheme="purple"
              onChange={(index) =>
                setActiveUserType(index === 0 ? "faculty" : "admin")
              }
            >
              <TabList mb="1em">
                <Tab>Faculty</Tab>
                <Tab>Admin</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                  <Box>
                    <Heading size="xl" mb={2} textAlign="left">
                      {userTypes.faculty.title}
                    </Heading>
                    <Text color="gray.600" textAlign="left">
                      {userTypes.faculty.welcomeText}
                    </Text>
                  </Box>
                </TabPanel>
                <TabPanel>
                  <Box>
                    <Heading size="xl" mb={2} textAlign="left">
                      {userTypes.admin.title}
                    </Heading>
                    <Text color="gray.600" textAlign="left">
                      {userTypes.admin.welcomeText}
                    </Text>
                  </Box>
                </TabPanel>
              </TabPanels>
            </Tabs>

            <form onSubmit={handleSubmit}>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Email address</FormLabel>
                  <Input
                    name="email"
                    type="email"
                    placeholder="Enter your email"
                    size="lg"
                    p={7}
                    borderRadius="md"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <Input
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    size="lg"
                    p={7}
                    value={formData.password}
                    onChange={handleChange}
                    borderRadius="md"
                  />
                </FormControl>

                <Flex justify="space-between" w="100%" align="center">
                  <Checkbox
                    colorScheme="purple"
                    name="rememberMe"
                    isChecked={formData.rememberMe}
                    onChange={handleChange}
                  >
                    Remember me
                  </Checkbox>
                  <Link color="purple.500" fontSize="sm">
                    Forgot password?
                  </Link>
                </Flex>

                <Button
                  type="submit"
                  w="100%"
                  size="lg"
                  bg="purple.500"
                  color="white"
                  _hover={{ bg: "purple.600" }}
                  borderRadius="md"
                >
                  Sign In as{" "}
                  {activeUserType === "faculty" ? "Faculty" : "Admin"}
                </Button>
              </VStack>
            </form>
          </VStack>
        </Container>
      </Flex>
    </Flex>
  );
};

// Mock login function - replace with actual API call
const loginUser = async (formData, userType) => {
  // Simulate API call
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (formData.email && formData.password) {
        resolve({
          success: true,
          token: "mock-token-123",
          userType: userType,
        });
      } else {
        reject(new Error("Invalid credentials"));
      }
    }, 1000);
  });
};

export default LoginPage;
