import wx
import requests
import re
import json
import frame
from pyswip import Prolog

# Helper function to enumerate all options and return them as dict and list
def list_to_dict(lst):
    d = {}
    l = list(set(lst))

    for i in range(len(l)):
        d[i] = l[i]

    return d, l


class MainFrame(frame.botframe):
    def __init__(self):
        frame.botframe.__init__(self, None)

        # Start with a welcome message
        self.chat_window.AppendText("BOT: Hello, I am FoodBot! I will help you to find your next recipe.\n")

        # Download json with receipes data and initialize Prolog KB
        self.recipes = self.download_recipes()
        self.prolog = self.initialize_prolog()

        # Placeholder for user choices
        self.cu = None
        self.ing = None
        self.effort = None
        self.course = None
        self.goal = None
        self.calories = None
        self.diet = None

        # Ask first Question
        self.current_question = 0
        self.prepare_question()

        self.goal_choices = []


    def download_recipes(self):
        recipes = []

        # get data
        r = requests.get(
            "https://gist.githubusercontent.com/pierre-minerva/70bccece0820fa839b53c264cc7460a3/raw/8c7afccd58cf78b42b99ceb0927025896ea108fa/recipe_data.json")
        # Save db
        with open('recipes.json', 'wb') as f:
            f.write(r.content)

        # process data
        with open('recipes.json') as f:
            for jsonObj in f:
                recipesDict = json.loads(jsonObj)
                recipes.append(recipesDict)

        return recipes

    def initialize_prolog(self):
        prolog = Prolog()

        # Adding of data to KB
        for recipe in self.recipes:
            # recipe
            title = recipe['page']['title']
            # diet
            for diet in recipe['page']['recipe']['diet_types']:
                prolog.assertz(f"diet('{title}','{diet}')")
            # protein
            protein = int(re.search(r'\d+', self.recipes[0]['page']['recipe']['nutrition_info'][2]).group())
            prolog.assertz(f"protein('{title}',{protein})")
            # calories
            calories = int(re.search(r'\d+', self.recipes[0]['page']['recipe']['nutrition_info'][1]).group())
            prolog.assertz(f"calories('{title}',{calories})")
            # time
            total_time = (recipe['page']['recipe']['cooking_time'] + self.recipes[0]['page']['recipe']['prep_time']) // 60
            prolog.assertz(f"time('{title}',{total_time})")
            # effort
            skill_level = recipe['page']['recipe']['skill_level']
            prolog.assertz(f"effort('{title}','{skill_level}')")
            # type
            for course in recipe['page']['recipe']['courses']:
                prolog.assertz(f"course('{title}','{course}')")
            # ingredients
            for ing in recipe['page']['recipe']['ingredients']:
                prolog.assertz(f"ing('{title}','{ing}')")
            # cuisine
            cuisine = recipe['page']['recipe']['cusine']
            prolog.assertz(f"cuisine('{title}','{cuisine}')")
            # recipe
            prolog.assertz(
                f"recipe('{title}','{diet}',{protein},{calories},{total_time},'{skill_level}','{course}','{ing}','{cuisine}' )")

        prolog.assertz("more(X,Y) :- X @> Y")

        # Q1
        prolog.assertz("diet(D)")

        # Q2
        prolog.assertz("goal(G)")

        # Q3
        prolog.assertz("protein(R) :- goal('Nutrition'); protein(R,P); more(P,20)")

        # Q6
        # if loss then no dessert

        prolog.assertz("recipe2(R,D,Ci,Ti,E,Co,I,Cu)")
        prolog.assertz(
            "recipe2(R,D,Ci,Ti,E,Co,I,Cu) :- recipe(R,D,P,C,T,E,Co,I,Cu); more(T,Ti); goal('Weight-Loss'); more(Ci,C); dif(Co,'Dessert')")
        prolog.assertz(
            "recipe2(R,D,Ci,Ti,E,Co,I,Cu) :- recipe(R,D,P,C,T,E,Co,I,Cu); more(T,Ti); goal('Weight-Gain'); more(C,Ci); dif(Co,'Snack')")
        prolog.assertz(
            "recipe2(R,D,Ci,Ti,E,Co,I,Cu) :- recipe(R,D,P,C,T,E,Co,I,Cu); more(T,Ti); goal('Nutrition'); more(P,20); dif(Co,'Dessert')")
        prolog.assertz("recipe2(R,D,Ci,Ti,E,Co,I,Cu) :- recipe(R,D,P,C,T,E,Co,I,Cu); more(T,Ti); goal('Pleasure')")
        return prolog

    def prepare_question(self):
        self.current_question += 1

        # IF Q1
        if self.current_question == 1:
            diets = []

            # Get all responses from Prolog
            for soln in self.prolog.query("diet(R,D)"):
                if "_" not in str(soln["D"]):
                    diets.append(str(soln["D"]))

            diets_dict, diets_lst = list_to_dict(diets)
            self.chat_window.AppendText("BOT: Do you have any dietary preferences?\n")
            # Update option in SelectBox
            self.listbox_options.Set(diets_lst)

        # IF Q2
        elif self.current_question == 2:
            choices = ["Weight-Loss", "Weight-Gain", "Nutrition", "Pleasure"]
            self.chat_window.AppendText("BOT: What is your dietary goal?\n")
            self.listbox_options.Set(choices)
        elif self.current_question == 3:
            # Show this question only if "Weight-Loss" or "Weight-Gain", else skip
            if "Weight-Loss" in self.goal_choices or "Weight-Gain" in self.goal_choices:
                self.chat_window.AppendText("BOT: What are your target calories?\n")
                self.edit_number.Show()
                self.listbox_options.Hide()
                self.listbox_options.GetParent().Layout()
            else:
                self.prepare_question()

        # Q4
        elif self.current_question == 4:
            self.chat_window.AppendText("BOT: How many minutes do you have to make the food?\n")
            self.edit_number.SetValue(30)
            self.edit_number.Show()
            self.listbox_options.Hide()
            self.listbox_options.GetParent().Layout()

        # Q5
        elif self.current_question == 5:
            effort = []
            for soln in self.prolog.query(
                    f"recipe2(R,'{self.diet}',{self.calories},{self.time},E,Co,I, Cu)"):
                if "_" not in str(soln["E"]):
                    effort.append(str(soln["E"]))
            effort_dict, effort_lst = list_to_dict(effort)
            self.chat_window.AppendText("BOT: How much effort do you want to put in?\n")
            self.listbox_options.Set(effort_lst)

        # Q6
        elif self.current_question == 6:
            course = []
            for soln in self.prolog.query(
                    f"recipe2(R,'{self.diet}',{self.calories},{self.time},'{self.effort}',Co,I, Cu)"):
                if str(soln["Co"]) in ["Snack", "Main course", "Dessert", "Breakfast"]:
                    course.append(str(soln["Co"]))
            effort_dict, effort_lst = list_to_dict(course)
            self.chat_window.AppendText("BOT: What course would you like?\n")
            self.listbox_options.Set(effort_lst)

        # Q7
        elif self.current_question == 7:
            ing = []

            for soln in self.prolog.query(
                    f"recipe2(R,'{self.diet}',{self.calories},{self.time},'{self.effort}','{self.course}',I, Cu)"):
                if "_" not in str(soln["I"]):
                    ing.append(str(soln["I"]))

            ing_dict, ing_lst = list_to_dict(ing)
            self.chat_window.AppendText("BOT: Which of these remaining ingredients would you like to be in your meal?\n")
            self.listbox_options.Set(ing_lst)

        # Q8
        elif self.current_question == 8:
            cuisine = []

            for soln in self.prolog.query(
                    f"recipe2(R,'{self.diet}',{self.calories},{self.time},'{self.effort}','{self.course}','{self.ing}', Cu)"):
                if "_" not in str(soln["Cu"]):
                    cuisine.append(str(soln["Cu"]))

            cuisine_dict, cuisine_lst = list_to_dict(cuisine)
            self.chat_window.AppendText("BOT: What cuisine do you want?\n")
            self.listbox_options.Set(cuisine_lst)

        # Time to make a final decission
        elif self.current_question == 9:
            self.make_decission()


        if self.listbox_options.GetCount() ==0:
            self.chat_window.AppendText("BOT: Unfortunately, we haven´t found any available receipe for you. Please try again with different answers.\n")

        # If there is only one option available, select it automatically
        if self.listbox_options.GetCount() == 1:
            self.btn_sendOnButtonClick(None,0)


    def btn_sendOnButtonClick( self, event, selected=None):
        """
        Evaluate selected answer and send it to Prolog
        """
        if selected is not None:
            self.listbox_options.SetSelection(selected)
        selected = self.listbox_options.GetStringSelection()
        selected = [selected]
        if len(selected)==0 and self.current_question not in [3]:
            wx.MessageBox("Please select at least one option.","No Option Selected", wx.ICON_INFORMATION)
            return False
        else:
            if self.current_question == 1:
                for choice in selected:
                    self.prolog.assertz(f"diet('{choice}')")
                self.chat_window.AppendText("YOU: "+", ".join(selected) + "\n")
                self.diet = choice
            elif self.current_question == 2:
                for choice in selected:
                    self.prolog.assertz(f"goal_dict('{choice}')")
                self.chat_window.AppendText("YOU: " + ", ".join(selected)+ "\n")
                self.goal_choices = selected
                self.goal = choice
            elif self.current_question == 3:
                calories = self.edit_number.GetValue()
                self.prolog.assertz(f"goal_dict('{calories}')")
                self.chat_window.AppendText(f"YOU: {calories} Calories\n")
                self.calories = calories

                self.edit_number.Hide()
                self.listbox_options.Show()
                self.listbox_options.GetParent().Layout()
            elif self.current_question == 4:
                time = self.edit_number.GetValue()
                self.prolog.assertz(f"time('{time}')")
                self.chat_window.AppendText(f"YOU: {time} Minutes\n")
                self.time = time

                self.edit_number.Hide()
                self.listbox_options.Show()
                self.listbox_options.GetParent().Layout()
            elif self.current_question == 5:
                for choice in selected:
                    self.prolog.assertz(f"effort('{choice}')")
                self.chat_window.AppendText("YOU: " + ", ".join(selected)+ "\n")
                self.effort = choice
            elif self.current_question == 6:
                for choice in selected:
                    self.prolog.assertz(f"course('{choice}')")
                self.chat_window.AppendText("YOU: " + ", ".join(selected)+ "\n")
                self.course = choice
            elif self.current_question == 7:
                for choice in selected:
                    self.prolog.assertz(f"ing('{choice}')")
                self.chat_window.AppendText("YOU: " + ", ".join(selected)+ "\n")
                self.ing = choice
            elif self.current_question == 8:
                self.chat_window.AppendText("YOU: " + ", ".join(selected[0])+ "\n")
                self.cu = selected[0]



        # Update the layout of the app. Usefull when we changed the size of the app or show/hiden some elements
        self.listbox_options.GetParent().Layout()
        self.prepare_question()

    def make_decission(self):
        """Make final Prolog query to find the receipes"""
        final_recipes = []
        for soln in self.prolog.query(
                f"recipe2(R,'{self.diet}',{self.calories},{self.time},'{self.effort}','{self.course}','{self.ing}', '{self.cu}')"):
            if type(soln["R"]) == type("str"):
                final_recipes.append(soln["R"])

        final_recipes_dict, final_recipes_lst = list_to_dict(final_recipes)

        # Show the results
        self.chat_window.AppendText("BOT: Nice, I found something for you 😀. The following recipes from BBC's Good Foods website match your needs:\n")
        for receipe in final_recipes_lst:
            self.chat_window.AppendText(receipe.replace("&amp;","&") + "\n")


