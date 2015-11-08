// 
// main.cpp
// 
// Created by Anthony Dervish on 2015-11-08
// Copyright (c) 2015 Dervish Software. All rights reserved.
// 


#include <iostream>
#include <gtest/gtest.h>


using namespace std;

// MAIN
// ----
int sum(int a, int b) {return a+b;}

TEST(Sum, Normal) {
  EXPECT_EQ(5, sum(2, 3));
}

int main(int argc, char **argv) {
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

