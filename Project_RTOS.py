import pygame, sys, os, random
import data.engine as e
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

s_width = 600
s_height = 400
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30
WINDOW_SIZE = (s_width,s_height)
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height
screen = pygame.display.set_mode(WINDOW_SIZE,0,32)
#set name for windown
pygame.display.set_caption('Project RTOS')
#import image
bri_img = pygame.image.load('data/images/bri_1.png')
bri_2_img = pygame.image.load('data/images/bri_2.png')
bri_3_img = pygame.image.load('data/images/bri_3.png')
cau_img = pygame.image.load('data/images/cau_0.png')
top_img = pygame.image.load('data/images/top.png')
top1_img = pygame.image.load('data/images/top_1.png')
top2_img = pygame.image.load('data/images/top_2.png')
grass_img = pygame.image.load('data/images/grass.png')
cherry_img =pygame.image.load('data/images/cherry-1.png')
bg_img = pygame.image.load('data/images/bg.png')
block_img = pygame.image.load('data/images/block.png')
game_over = pygame.image.load('data/images/game_over.png')
win_game = pygame.image.load('data/images/win_game.png')
dirt_img = pygame.image.load('data/images/dirt.png')
plant_img = pygame.image.load('data/images/plant.png')
gem_img = pygame.image.load('data/images/gem.png')
spikes_img = pygame.image.load('data/images/spikes.png')
start_img = pygame.image.load('data/images/start.png')
start_1_img = pygame.image.load('data/images/start_1.png')
stop_img = pygame.image.load('data/images/stop.png')
stop_1_img = pygame.image.load('data/images/stop_1.png')
continue_img = pygame.image.load('data/images/continue.png')
continue_1_img = pygame.image.load('data/images/continue_1.png')
quit_img = pygame.image.load('data/images/quit.png')
quit_1_img = pygame.image.load('data/images/quit_1.png')
jumper_img = pygame.image.load('data/images/jumper.png').convert()
jumper_img.set_colorkey((255,255,255))
bg = pygame.image.load('data/images/back.png')
# this function use for create text on bottom of the screen game
def draw_text_bottom(surface, text, size, color):
        font = pygame.font.SysFont('comicsans', size, bold=True)
        label = font.render(text, 1, color)

        surface.blit(label, (top_left_x + play_width/ 0.8 - (label.get_width() / 1.1), top_left_y + play_height/1.2 - label.get_height()/1.1))
#this func use for load key map in map.txt
def load_map(path):
        f= open(path + '.txt','r')
        data = f.read()
        f.close()
        data = data.split('\n') # xuong dong trong file map
        game_map = []
        for row in data:
            game_map.append(list(row))
        return game_map
#class for jumping obj
class jumper_obj():
        def __init__(self, loc):
            self.loc = loc
#render vật thể và có thêm biến scroll để vật thể có thể di chuyển theo cam
        def render(self, surf, scroll):
            surf.blit(jumper_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))
#tạo hit box
        def get_rect(self):
            return pygame.Rect(self.loc[0], self.loc[1], 8, 9)
#test sự va chạm giữa vật thể và player
        def collision_test(self, rect):
            jumper_rect = self.get_rect()
            return jumper_rect.colliderect(rect)
class spiker_obj():
        def __init__(self, loc):
            self.loc = loc

        def render(self, surf, scroll):
            surf.blit(spikes_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

        def get_rect(self):
            return pygame.Rect(self.loc[0], self.loc[1], 80, 10)

        def collision_test(self, rect):
            jumper_rect = self.get_rect()
            return jumper_rect.colliderect(rect)
class win_obj():
        def __init__(self, loc):
            self.loc = loc

        def render(self, surf, scroll):
            surf.blit(cherry_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

        def get_rect(self):
            return pygame.Rect(self.loc[0], self.loc[1], 21, 21)

        def collision_test(self, rect):
            jumper_rect = self.get_rect()
            return jumper_rect.colliderect(rect)
class gem_obj(pygame.sprite.Sprite):
        def __init__(self, loc,*groups):   
            self.time = True
            self.image = gem_img
            self.loc = loc
            pygame.sprite.Sprite.__init__(self)

        def render(self, surf, scroll):
            surf.blit(self.image, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

        def get_rect(self):
            return pygame.Rect(self.loc[0], self.loc[1], 15, 13)

        def collision_test(self, rect):
            jumper_rect = self.get_rect()
            return jumper_rect.colliderect(rect)
        
        def update(self):
                if self.time is not None:  # If the timer has been started...
            # and 500 ms have elapsed, kill the sprite.
                    if pygame.time.get_ticks() - self.time >= 500:
                        self.kill()
        


###hàm main
def main(screen):
    moving_right = False
    moving_left = False
    vertical_momentum = 0
    air_timer = 0
    run = True
    display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled
    grass_sound_timer = 0 #timer cho âm của tiếng di chuyển
    true_scroll = [0,0]# biến vị trí của cam
    all_sprites = pygame.sprite.Group()
    gem = gem_obj((320, 240), all_sprites)

    e.load_animations('data/images/entities/')#load animationg trong thư viện animation sẽ được lưu trong entities.txt
    
    game_map = load_map('map')
    tile_index = {1:grass_img,
                  2:dirt_img,
                  3:plant_img
                  }
#import sound từ dường dẫn data/audio hàm pygame.mixer.Sound là hàm load
    jump_sound = pygame.mixer.Sound('data/audio/jumb.wav')
    quit_sound = pygame.mixer.Sound('data/audio/quit.wav')
    die_sound = pygame.mixer.Sound('data/audio/die.wav')
    cherry_sound = pygame.mixer.Sound('data/audio/cherry.wav')
    hit_sound = pygame.mixer.Sound('data/audio/enemyjump.wav')
    
    grass_sounds = [pygame.mixer.Sound('data/audio/walk_0.wav'),pygame.mixer.Sound('data/audio/walk_1.wav')]

    pygame.mixer.music.load('data/audio/music.wav')
    pygame.mixer.music.play(-1)

    grass_sound_timer = 0

    player = e.entity(300,200,17,22,'player')#tạo player bằng thư viện engine
#gọi và xác định các obj
    enemies = []

    enemies.append([0,e.entity(870,200,13,13,'enemy')])
    enemies.append([0,e.entity(1100,200,13,13,'enemy')])
    enemies.append([0,e.entity(1700,260,13,13,'enemy')])
    

  
    jumper_objects = []
    jumper_objects.append(jumper_obj((770,120)))
    jumper_objects.append(jumper_obj((1720,200)))
    jumper_objects.append(jumper_obj((2680,200)))
    jumper_objects.append(jumper_obj((6710,160)))

    spike_objects = []
    spike_objects.append(spiker_obj((745,300)))
    spike_objects.append(spiker_obj((745,300)))
    spike_objects.append(spiker_obj((2610,300)))
    spike_objects.append(spiker_obj((2690,300)))
    spike_objects.append(spiker_obj((3090,320)))
    spike_objects.append(spiker_obj((3420,320)))
    spike_objects.append(spiker_obj((4420,300)))
    spike_objects.append(spiker_obj((4500,300)))
    spike_objects.append(spiker_obj((4580,300)))
    spike_objects.append(spiker_obj((2670,300)))
    spike_objects.append(spiker_obj((1700,260)))
    spike_objects.append(spiker_obj((870,200)))
    spike_objects.append(spiker_obj((6660,300)))
    spike_objects.append(spiker_obj((6728,300)))
    
    cherry_objects = [] 
    cherry_objects.append(win_obj((6900,190)))

    gem_objects = []
    gem_objects.append(gem_obj((200,180)))
    
    while run: # game loop
        display.blit(bg_img,(0,0)) # clear screen by filling it with bg

        if grass_sound_timer > 0:
            grass_sound_timer -= 1
#xác định ví trị của cam sao cho vào đúng giữa nhân vật 300/2+ chiều cao/2, 200/2 công chiều rộng/2 chia 20 dùng để tránh hiện tượng xé hình
        true_scroll[0] += (player.x-true_scroll[0]-158)/20
        true_scroll[1] += (player.y-true_scroll[1]-111)/20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])


#xác định các biên trong file map.txt để quy đổi sang hình ảnh đã import mỗi block có giá trị 16x16
        tile_rects = []
        y=0
        for layer in game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    display.blit(dirt_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '2':
                    display.blit(grass_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '3':
                    display.blit(block_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '4':
                    display.blit(top_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '5':
                    display.blit(top1_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '6':
                    display.blit(top2_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '7':
                    display.blit(wood_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '7':
                    display.blit(cau_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '8':
                    display.blit(bri_2_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile == '9':
                    display.blit(bri_3_img,(x*16-scroll[0],y*16-scroll[1]))
                if tile != '0':
                    tile_rects.append(pygame.Rect(x*16,y*16,16,16))
                x += 1
            y += 1
#tạo hành động cho nhanh vật và add thêm animation
        player_movement = [0,0]
        if moving_right == True:
            player_movement[0] += 2
        if moving_left == True:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player.set_action('idle')
        if player_movement[0] > 0:
            player.set_flip(False)
            player.set_action('run')
        if player_movement[0] < 0:
            player.set_flip(True)
            player.set_action('run')
        if player_movement[1] < 0 and player_movement[0] < 0:
            player.set_action('jump')
            player.set_flip(True)
        if player_movement[1] < 0 and player_movement[0] > 0:
            player.set_action('jump')
            player.set_flip(False)
            
#check sự va chạm của nhân vật với các block
        collision_types = player.move(player_movement,tile_rects)

        if collision_types['bottom'] == True:
            air_timer = 0
            vertical_momentum = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        else:
            air_timer += 1

        player.change_frame(1)
        player.display(display,scroll)
#vòng lặp cho các obj phía trên dùng cho những việc cụ thể. Test sự va chạm và nếu có sẽ chạy điều kiện lập trình
        for jumper in jumper_objects:
            jumper.render(display,scroll)
            if jumper.collision_test(player.obj.rect):
                vertical_momentum = -5
                hit_sound.play()
                
        for spiker in spike_objects:
            spiker.render(display,scroll)
            if spiker.collision_test(player.obj.rect):
                player.set_action('die')
                pygame.mixer.music.fadeout(10)
                die_sound.play()
                pygame.time.delay(300)
                gameover(screen)
                
        for cherry in cherry_objects:
            cherry.render(display,scroll)
            if cherry.collision_test(player.obj.rect):
                pygame.mixer.music.fadeout(10)
                cherry_sound.play()
                pygame.time.delay(300)
                wingame(screen)
                
        for gem in gem_objects:
            gem.render(display,scroll)
            if gem.collision_test(player.obj.rect):
                gem_obj.time = pygame.time.get_ticks()
                hit_sound.play()

        display_r = pygame.Rect(scroll[0],scroll[1],300,200)
#tạo ra các enemy và check sự va chamj của chúng với mặt đất để chúng không bị rớt ra khỏi bản đồ
        for enemy in enemies:
            if display_r.colliderect(enemy[1].obj.rect):
                enemy[0] += 0.2
                if enemy[0] > 3:
                    enemy[0] = 3
                enemy_movement = [0,enemy[0]]
                if player.x > enemy[1].x + 5:
                    enemy_movement[0] = 1
                if player.x < enemy[1].x - 5:
                    enemy_movement[0] = -1
                collision_types = enemy[1].move(enemy_movement,tile_rects)
                if collision_types['bottom'] == True:
                    enemy[0] = 0

                enemy[1].display(display,scroll)

                if player.obj.rect.colliderect(enemy[1].obj.rect):
                    player.set_action('die')
                    pygame.mixer.music.fadeout(10)
                    die_sound.play()
                    pygame.time.delay(300)
                    gameover(screen)

#set key cho game
        for event in pygame.event.get(): # event loop
            if event.type == QUIT:
                pygame.mixer.music.stop()
                quit_sound.play()
                pygame.time.delay(1600)
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_m:
                    pygame.mixer.music.fadeout(1000)
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_ESCAPE:
                        pygame.mixer.music.fadeout(10)
                        quit_sound.play()
                        pygame.time.delay(1600)
                        main_menu(screen)
                if event.key == K_SPACE:
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_momentum = -5
                        
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False
        all_sprites.update()
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        screen.blit(pygame.transform.scale(display,WINDOW_SIZE),(0,0))
        pygame.display.update()
        clock.tick(60)
#hàm game over
def gameover(screen):  # *
    run = True
    ui2_sound = pygame.mixer.Sound('data/audio/ui2.wav')
    quit_sound = pygame.mixer.Sound('data/audio/quit.wav')
    pygame.mixer.music.load('data/audio/gameover_theme.wav')
    pygame.mixer.music.play(-1)
    while run:
        screen.blit(game_over,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                quit_sound.play()
                pygame.time.delay(1600)
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                        pygame.mixer.music.fadeout(10)
                        quit_sound.play()
                        pygame.time.delay(800)
                        main(screen)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if s_width/2.5 <= mouse[0] <= s_width/2.5+150 and s_height/1.28 <= mouse[1] <= s_height/1.28+50: 
                        pygame.mixer.music.fadeout(10)
                        ui2_sound.play()
                        pygame.time.delay(800)
                        main(screen)
                if s_width/2.5<= mouse[0] <= s_width/2.5+150 and s_height/1.15 <= mouse[1] <= s_height/1.15+50: 
                        pygame.mixer.music.fadeout(10)
                        quit_sound.play()
                        pygame.time.delay(1600)
                        pygame.quit()
                        sys.exit()
        mouse = pygame.mouse.get_pos()
##        print(mouse) #debug vi tri chuot
        # nut bam trong menu 
        if s_width/2.5 <= mouse[0] <= s_width/2.5+106 and s_height/1.28 <= mouse[1] <= s_height/1.28+22: 
                screen.blit(continue_1_img,([s_width/2.5,s_height/1.28]))
        else:
                screen.blit(continue_img,([s_width/2.5,s_height/1.28]))
        
        if s_width/2.5 <= mouse[0] <= s_width/2.5+105 and s_height/1.15 <= mouse[1] <= s_height/1.15+21: 
                screen.blit(quit_1_img,([s_width/2.5,s_height/1.15]))
        else:
                screen.blit(quit_img , (s_width/2.5,s_height/1.15))
        pygame.display.update()

    pygame.display.quit()
def wingame(screen):  # *
    run = True
    ui2_sound = pygame.mixer.Sound('data/audio/ui2.wav')
    quit_sound = pygame.mixer.Sound('data/audio/quit.wav')
    pygame.mixer.music.load('data/audio/finalsound.mp3')
    pygame.mixer.music.play()
    while run:
        screen.blit(win_game,(0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                quit_sound.play()
                pygame.time.delay(1600)
                run = False
            if event.type == pygame.KEYDOWN:
                pygame.mixer.music.fadeout(10)
                ui2_sound.play()
                pygame.time.delay(800)
                main_menu(screen)

    pygame.display.quit()
def main_menu(screen):  # *
    run = True
    ui_sound = pygame.mixer.Sound('data/audio/menu_ui.wav')
    quit_sound = pygame.mixer.Sound('data/audio/quit.wav')
    pygame.mixer.music.load('data/audio/menu.wav')
    pygame.mixer.music.play(-1)
    color = (255,255,255)
    color_light = (170,170,170)
    color_dark = (100,100,100)
    smallfont = pygame.font.SysFont('comicsans',35)
    text = smallfont.render('NewGame' , True , color)
    text_2 = smallfont.render('Quit' , True , color)
    while run:
        screen.blit(bg,(0,0))
##        draw_text_bottom(screen, 'Press Any Key To Play', 60, (255,255,255))
##        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                quit_sound.play()
                pygame.time.delay(1600)
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                        pygame.mixer.music.fadeout(10)
                        quit_sound.play()
                        pygame.time.delay(1600)
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if s_width/2 <= mouse[0] <= s_width/2+150 and s_height/2 <= mouse[1] <= s_height/2+50: 
                        pygame.mixer.music.fadeout(10)
                        ui_sound.play()
                        pygame.time.delay(800)
                        main(screen)
                if s_width/2.5<= mouse[0] <= s_width/2.5+150 and s_height/1.45 <= mouse[1] <= s_height/1.45+50: 
                        pygame.mixer.music.fadeout(10)
                        quit_sound.play()
                        pygame.time.delay(1600)
                        pygame.quit()
                        sys.exit()
        mouse = pygame.mouse.get_pos()
##        print(mouse) debug vi tri chuot
        # nut bam trong menu 
        if s_width/2 <= mouse[0] <= s_width/2+150 and s_height/2 <= mouse[1] <= s_height/2+50: 
                screen.blit(start_1_img,([s_width/2.5,s_height/2]))
        else:
                screen.blit(start_img,([s_width/2.5,s_height/2]))
        
        if s_width/2.5 <= mouse[0] <= s_width/2.5+150 and s_height/1.45 <= mouse[1] <= s_height/1.45+50: 
                screen.blit(stop_1_img,([s_width/2.5,s_height/1.45]))
        else:
                screen.blit(stop_img , (s_width/2.5,s_height/1.45))
        pygame.display.update() 
  

    pygame.display.quit()
main_menu(screen)
gameover(screen)
wingame(screen)

