import math

total_states = 0

for white_occupied in range(1, 16):
    for black_occupied in range(1, min(15, 24 - white_occupied) + 1):
        ways_white_points = math.comb(24, white_occupied) # ways to choose white_occupied points
        ways_black_points = math.comb(24 - white_occupied, black_occupied) # ways to choose black_occupied points
        for white_tokens_in_game in range(1, 16):
            for black_tokens_in_game in range(1, 16):
                ways_white_tokens = math.comb(white_tokens_in_game - 1, white_occupied - 1) # ways to distribute 15 tokens on white_occupied points (at least 1 token per point)
                ways_black_tokens = math.comb(black_tokens_in_game - 1, black_occupied - 1) # ways to distribute 15 tokens on black_occupied points (at least 1 token per point)
                multiplier = 1
                if white_tokens_in_game != 15:
                    multiplier *= 15 - white_tokens_in_game + 1
                if black_tokens_in_game != 15:
                    multiplier *= 15 - black_tokens_in_game + 1

                total_states += ways_white_points * ways_black_points * ways_white_tokens * ways_black_tokens * multiplier

print("Total states:", total_states)
print("Total states * dice outcomes:", total_states * 21)