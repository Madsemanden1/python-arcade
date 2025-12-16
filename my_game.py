"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""

import arcade, random

# Import sprites from local file my_sprites.py
from my_sprites import Player, PlayerShot

# Set the scaling of all sprites in the game
SPRITE_SCALING = 0.5

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player
PLAYER_LIVES = 3
PLAYER_SPEED_FORWARDS = 30
PLAYER_SPEED_BACKWARDS = PLAYER_SPEED_FORWARDS
PLAYER_SPEED_ANGLE = 200
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 300

KEYS_FIRE = [arcade.key.SPACE, arcade.key.RSHIFT]
KEYS_RIGHT = [arcade.key.D, arcade.key.RIGHT]
KEYS_LEFT = [arcade.key.A, arcade.key.LEFT]
KEYS_UP = [arcade.key.W, arcade.key.UP]
KEYS_DOWN = [arcade.key.S, arcade.key.DOWN]
KEYS_RESET = [arcade.key.SPACE]

WALLS = 15 #set to 15 for normal game

P1_KEYS = {
    arcade.key.A: "LEFT",
    arcade.key.D: "RIGHT",
    arcade.key.W: "UP",
    arcade.key.S: "DOWN",
    arcade.key.E: "FIRE"
}

P2_KEYS = {
    arcade.key.LEFT: "LEFT",
    arcade.key.RIGHT: "RIGHT",
    arcade.key.UP: "UP",
    arcade.key.DOWN: "DOWN",
    arcade.key.PAGEUP: "FIRE"
}


class GameView(arcade.View):
    """
    The view with the game itself
    """

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set up the player info
        self.player_lives = PLAYER_LIVES

        # Create a Player object
        p1 = Player(
            center_x=PLAYER_START_X,
            center_y=50,
            min_x_pos=0,
            max_x_pos=SCREEN_WIDTH,
            max_y_pos=600,
            min_y_pos=0,
            scale=SPRITE_SCALING,
            controls=P1_KEYS,
            color=[225,155,155],
            name="Player 1"
        )

        p2 = Player(
            center_x=PLAYER_START_X,
            center_y=SCREEN_HEIGHT-50,
            min_x_pos=0,
            max_x_pos=SCREEN_WIDTH,
            max_y_pos=600,
            min_y_pos=0,
            scale=SPRITE_SCALING,
            angle=-90,
            controls=P2_KEYS,
            color=[152,148,255],
            name="Player 2"
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(p1)
        self.player_list.append(p2)


        self.walls_list = arcade.SpriteList()

# vælger et tal mellem 1 og 2
        s = random.random()+1

        t = arcade.make_soft_square_texture(
            size=100,
            center_alpha=255,
            outer_alpha=255,
            color=[255, 255, 255]
        )

        cw = arcade.Sprite(
            center_x=400,
            center_y=300,
            filename="images/UI/buttonBlue.png",
            scale=s/3,
            angle=0,
            texture=t
        )
        self.walls_list.append(cw)

        for i in range(WALLS):
            s = random.random()+1
            a = random.choice([0, 90])

            w = arcade.Sprite(
                center_x=random.randint(0,SCREEN_WIDTH),
                center_y=random.randint(150, SCREEN_HEIGHT-150),
                filename= "images/UI/buttonBlue.png",
                scale=s/3,
                angle=a,
            )

            self.walls_list.append(w)



        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """

        # Clear screen so we can draw new stuff
        self.clear()

        # Draw the player sprites
        for p in self.player_list:
            p.shots_list.draw()
            p.draw()

        self.walls_list.draw()

        for i, p in enumerate(self.player_list, 1):
            arcade.draw_text(
                f"player {i} lives left: {p.lives}",
                start_x=10,
                start_y=SCREEN_HEIGHT - i*20,
                color=arcade.color.WHITE
            )

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Only works when both players are alive
        if len(self.player_list) > 1:
            # Player speed decreases
            for player_no, p in enumerate(self.player_list):
                decrease = 0.9
                p.change_x *= decrease
                p.change_y *= decrease

                p.on_update(delta_time)
                p.shots_list.update()


                for other_player_to_check in self.player_list:
                    if other_player_to_check != p:
                        shots_hitting_me = p.collides_with_list(other_player_to_check.shots_list)
                        if len(shots_hitting_me) > 0:
                            p.lives -= 1
                            for s in shots_hitting_me:
                                s.kill()
                        if p.lives <= 0:
                            print(f"player {player_no+1} dead")
                            p.kill()



                # Remove shots that collide with walls
                for w in self.walls_list:
                    for s in w.collides_with_list(p.shots_list):
                        s.kill()

                # Player collides with walls (bounce!)
                    for w in self.walls_list:
                        if w.collides_with_sprite(p):
                            # Gives the player the opposite speed
                            p.change_x *= -1.2
                            p.change_y *= -1.2
                            # Moves the player out of the wall - important that this is last!
                            p.on_update(delta_time)

    def game_over(self):
        """
        Call this when the game is over
        """

        # Create a game over view
        game_over_view = GameOverView(self.player_list)

        # Change to game over view
        self.window.show_view(game_over_view)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        for p in self.player_list:
            p.on_key_press(key, modifiers)

        # End the game if the escape key is pressed
        if key == arcade.key.ESCAPE:
            self.game_over()


    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        for p in self.player_list:
            p.on_key_release(key, modifiers)

        if key in KEYS_UP:
            self.up_pressed = False
        elif key in KEYS_DOWN:
            self.down_pressed = False
        elif key in KEYS_LEFT:
            self.left_pressed = False
        elif key in KEYS_RIGHT:
            self.right_pressed = False

        if len(self.player_list) <= 1:
            if key in KEYS_RESET:
                self.game_over()


    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        if len(KEYS_FIRE) > 0:
            self.on_key_press(KEYS_FIRE[0], [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


class IntroView(arcade.View):
    """
    View to show instructions
    """

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.TAN)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """
        self.clear()

        # Draw some text
        arcade.draw_text(
            "The Game",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.AQUAMARINE,
            font_size=50,
            anchor_x="center",
        )

        # Draw more text
        arcade.draw_text(
            "Press any key to start the game",
            self.window.width / 2,
            self.window.height / 2 - 75,
            arcade.color.COOL_BLACK,
            font_size=20,
            anchor_x="center",
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Start the game when any key is pressed
        """
        self.game_start()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """
        Start the game when any mouse button is released
        """
        self.game_start()

    def game_start(self):
        self.window.show_view(GameView())


class GameOverView(arcade.View):
    """
    View to show when the game is over
    """

    def __init__(self, player_list, window=None):
        """
        Create a Game Over view. Pass the final score to display.
        """
        self.player_list = player_list

        super().__init__(window)

    def setup_old(self, score: int):
        """
        Call this from the game so we can show the score.
        """
        self.score = score

    def on_show_view(self):
        """
        This is run once when we switch to this view
        """

        # Set the background color
        arcade.set_background_color(arcade.csscolor.DARK_GOLDENROD)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """
        Draw this view
        """

        self.clear()

        # Draw some text
        arcade.draw_text(
            "Game over!",
            self.window.width / 2,
            self.window.height / 2,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )

        for p in self.player_list:
            p.draw()
            p.center_x = SCREEN_WIDTH/2
            p.center_y = 150
            p.angle = 90
            p.scale = 1.5

        for p in (self.player_list):
            arcade.draw_text(
                f"{p.name} won with {p.lives}/3 lives left!",
                self.window.width / 2,
                self.window.height / 2.5,
                arcade.color.LIGHT_BLUE,
                font_size=20,
                anchor_x="center",
            )


    def on_key_press(self, key: int, modifiers: int):
        """
        Return to intro screen when any key is pressed
        """
        intro_view = IntroView()
        self.window.show_view(intro_view)


def main():
    """
    Main method
    """
    # Create a window to hold views
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Game starts in the intro view
    start_view = IntroView()

    window.show_view(start_view)

    arcade.run()


if __name__ == "__main__":
    main()
