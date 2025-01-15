#include <iostream>
using namespace std;


void calculateAverageAndGrade(float testScores[], float testWeights[], int numberOfTests) {
    float totalScore = 0.0;
    float totalWeight = 0.0;

    
    for (int i = 0; i < numberOfTests; ++i) {
        if (testScores[i] < 0 || testScores[i] > 100 || testWeights[i] < 0 || testWeights[i] > 1) {
            cout << "Error: Invalid input\n";
            return;
        }
        totalScore += testScores[i] * testWeights[i];
        totalWeight += testWeights[i];
    }

    if (totalWeight == 0) {
        cout << "Error: Cannot divide by zero\n";
        return;
    }

    float averageScore = totalScore / totalWeight;

    char grade;
    if (averageScore >= 90) {
        grade = 'A';
    } else if (averageScore >= 80) {
        grade = 'B';
    } else if (averageScore >= 70) {
        grade = 'C';
    } else if (averageScore >= 60) {
        grade = 'D';
    } else {
        grade = 'F';
    }

    cout << "Average Score: " << averageScore << endl;
    cout << "Grade: " << grade << endl;
}

int main() {
    int numberOfTests;
    cout << "Enter the number of tests: ";
    cin >> numberOfTests;

    float testScores[numberOfTests];
    float testWeights[numberOfTests];

    cout << "Enter the test scores and their respective weights:\n";
    for (int i = 0; i < numberOfTests; ++i) {
        cout << "Test " << i+1 << " score: ";
        cin >> testScores[i];
        cout << "Test " << i+1 << " weight: ";
        cin >> testWeights[i];
    }

    calculateAverageAndGrade(testScores, testWeights, numberOfTests);

    return 0;
}
